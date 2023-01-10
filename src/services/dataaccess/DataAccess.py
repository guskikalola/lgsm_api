import mariadb
import sys
from services.domain import User
from services.domain import Server
from services.exceptions import ServerNameRepeatedException, GameNotExistsException
from services.utils import ServerList
from models import GameModel

class DataAccess:
    def __init__(self, user, password, host, database):

        self.conn_params = {
            "user": user,
            "password": password,
            "host": host,
            "database": database
        }
        self.connection = None
        self.cursor = None

    def initialize_db(self):
        self.open()

        sql = "SELECT * FROM USER"
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            self.close()
            return None
        except mariadb.Error as e:
            print("INITIALIZING DATABASE")

        self.connection.begin()
        create_procedure_create_user_sql = """
            CREATE DEFINER=CURRENT_USER PROCEDURE IF NOT EXISTS `CreateUser` (IN `username_p` VARCHAR(125) CHARSET utf8mb4, IN `full_name_p` VARCHAR(125) CHARSET utf8mb4, IN `email_p` VARCHAR(125) CHARSET utf8mb4, IN `hashed_password_p` VARCHAR(1000) CHARSET utf8mb4, IN `active_p` BOOLEAN)  COMMENT 'Creates a new user' BEGIN
                INSERT INTO USER(username, full_name, email, hashed_password, active) VALUES (username_p, full_name_p, email_p, hashed_password_p, active_p);
            END;
        """
        create_procedure_create_server_sql = """
            CREATE DEFINER=CURRENT_USER PROCEDURE IF NOT EXISTS `CreateServer` (IN `server_name_p` VARCHAR(125) CHARSET utf8mb4, IN `server_pretty_name_p` VARCHAR(125) CHARSET utf8mb4, IN `game_name_p` VARCHAR(125) CHARSET utf8mb4)  COMMENT 'Creates a new server' BEGIN
                INSERT INTO SERVER(server_name, server_pretty_name, game_name) VALUES (server_name_p,server_pretty_name_p, game_name_p);
            END;
        """

        create_procedure_delete_server_sql = """
            CREATE DEFINER=CURRENT_USER PROCEDURE IF NOT EXISTS `DeleteServer` (IN `server_name_p` VARCHAR(125) CHARSET utf8mb4)  COMMENT 'Deletes a server' BEGIN
                DELETE FROM SERVER where server_name = server_name_p;
            END;
        """

        create_procedure_create_game_sql = """
            CREATE DEFINER=CURRENT_USER PROCEDURE IF NOT EXISTS `CreateGame` (IN `gm_p` VARCHAR(15) CHARSET utf8mb4, IN `game_name_p` VARCHAR(125) CHARSET utf8mb4,IN `game_full_name_p` VARCHAR(125) CHARSET utf8mb4)  COMMENT 'Creates a game' BEGIN
                REPLACE INTO GAME(gm,game_name,game_full_name) VALUES (gm_p,game_name_p,game_full_name_p);
            END;
        """

        create_table_games_sql = """
            CREATE TABLE IF NOT EXISTS `GAME` (
                `game_name` varchar(125) NOT NULL PRIMARY KEY,
                `gm` varchar(15) NOT NULL,
                `game_full_name` varchar(125) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """

        create_table_users_sql = """
            CREATE TABLE IF NOT EXISTS `USER` (
                `username` varchar(125) NOT NULL PRIMARY KEY,
                `full_name` varchar(125) NULL,
                `email` varchar(125) NULL,
                `hashed_password` varchar(1000) NOT NULL,
                `active` tinyint(1) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """

        create_table_servers_sql = """
            CREATE TABLE IF NOT EXISTS `SERVER` (
                `server_name` VARCHAR(125) NOT NULL PRIMARY KEY, 
                `server_pretty_name` VARCHAR(125) NOT NULL, 
                `game_name` VARCHAR(125) NOT NULL,
                FOREIGN KEY (game_name) REFERENCES GAME(game_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """

        self.cursor.execute(create_procedure_create_user_sql)
        self.cursor.execute(create_procedure_create_server_sql)
        self.cursor.execute(create_procedure_delete_server_sql)
        self.cursor.execute(create_procedure_create_game_sql)
        self.cursor.execute(create_table_games_sql)
        self.cursor.execute(create_table_users_sql)
        self.cursor.execute(create_table_servers_sql)
        self.connection.commit()
        self.close()

    def open(self):
        try:
            self.connection = mariadb.connect(**self.conn_params)
        except mariadb.Error as e:
            # TODO: Logs system
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)
        self.cursor = self.connection.cursor()
        return self.cursor

    def close(self):
        if not self.cursor is None:
            self.cursor.close()
            self.cursor = None
        if not self.connection is None:
            self.connection.close()
            self.connection = None

    def load_game_list(self):
        self.connection.begin()
        for (gm, game_name, game_full_name) in ServerList():
            params = (gm, game_name, game_full_name)
            try:
                self.cursor.callproc("CreateGame", params)
            except mariadb.IntegrityError as e:
                print("[db.load_game_list] "+game_name + " skipped, its already created and has a server referencing it")
        self.connection.commit()

    def get_user(self, username: str) -> User | None:
        sql = "SELECT username,full_name,email,hashed_password,active FROM USER WHERE username = ?"
        self.cursor.execute(sql, [username])
        user = self.cursor.fetchone()
        if not user is None:
            return User(username=user[0], full_name=user[1], email=user[2], hashed_password=user[3].encode(), active=user[4])
        else:
            return None

    def get_server(self, server_name: str):
        sql = "SELECT server_name, server_pretty_name, game_name FROM SERVER WHERE server_name = ?"
        self.cursor.execute(sql, [server_name])
        server = self.cursor.fetchone()
        if not server is None:
            return Server(server_name=server[0], server_pretty_name=server[1], game_name=server[2])
        else:
            return None

    def get_all_servers(self):
        sql = "SELECT server_name, server_pretty_name,game_name FROM SERVER"
        self.cursor.execute(sql)
        servers = self.cursor.fetchall()
        if not servers is None:
            return [Server(server_name=server[0], server_pretty_name=server[1], game_name=server[2]) for server in servers]
        else:
            return None

    def create_user(self, username: str, hashed_password: str, full_name: str = "", email: str = "", active: bool = True):
        user = User(username=username, email=email, full_name=full_name,
                    hashed_password=hashed_password, active=active)
        parameters = (user.username, user.full_name, user.email,
                      user.hashed_password, user.active)
        try:
            self.connection.begin()
            self.cursor.callproc("CreateUser", parameters)
            self.connection.commit()
        except mariadb.Error as e:
            return e
        return user

    def create_server(self, server_name: str, server_pretty_name: str, game_name: str):
        """Create a new server

        Creates a new server entry in the database, creates the
        server folder and downloads the basic scripts from linuxgsm there.

        :param str server_name: Server unique identifier
        :param str server_pretty_name: Server pretty name
        :param str game_name: Name of the server's game
        """
        print(server_pretty_name)
        server = Server(
            server_name=server_name,
            server_pretty_name=server_pretty_name,
            game_name=game_name,
        )
        parameters = (server.server_name,
                      server.server_pretty_name, server.game_name)

        if not self.get_server(server_name) is None:
            raise ServerNameRepeatedException(
                "There is already a server with that name. ({})".format(server_name))

        try:
            self.connection.begin()
            self.cursor.callproc("CreateServer", parameters)
            self.connection.commit()
        except mariadb.IntegrityError as e:
            raise GameNotExistsException("No game exists with that name : " + server.game_name)
        except mariadb.Error:
            raise e
        return server

    def delete_server(self, server_name: str):
        """Delete a server

        Deletes the server from the database and filesystem

        :param str server_name: Server unique identifier
        """

        server = self.get_server(server_name)

        if server is None:
            return None

        parameters = (server.server_name,)

        try:
            self.connection.begin()
            self.cursor.callproc("DeleteServer", parameters)
            self.connection.commit()
        except mariadb.Error as e:
            raise e

        server.remove()

        return server

    def get_game_list(self):
        sql = "SELECT gm, game_name, game_full_name FROM GAME"
        self.cursor.execute(sql)
        games = self.cursor.fetchall()
        if not games is None:
            return [GameModel(gm=game[0], game_name=game[1], game_full_name=game[2]) for game in games]
        else:
            return None