from models import ServerModel
from models import ServerDetailsModel, ServerWithDetailsModel
import asyncio
from datetime import datetime
from services.utils import DockerComposeTemplate, ServerDetailsParser
from services.enums import ServerCommandsResponse, ServerStatusEnum
from services.utils import ConsoleStream
import re
import logging

logger = logging.getLogger(__name__)


async def run(command):
    logger.debug(command)
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout_bytes, stderr_bytes = await process.communicate()

    stdout = ""
    stderr = ""

    if stderr_bytes:
        stderr = stderr_bytes.decode()
    if stdout_bytes:
        stdout = stdout_bytes.decode()

    return (stdout, stderr, process)


class Server:
    """Class representing a game server

    This class is the representation of a game server and provides
    methods to interact with the server's container.

    """

    def __init__(self, server_name: str, server_pretty_name: str, game_name: str):
        """Create a new Server instance

        @param server_name Server unique identifier 
        @param server_pretty_name Server's pretty name
        @param game_name The game this server is hosting

        """
        self.server_name = server_name
        self.server_pretty_name = server_pretty_name
        self.game_name = game_name
        self.exec_path = "/servers/"+server_name

    async def download(self) -> bool:
        """Create the docker compose file from the template 

        Creates a directory at /servers/{server_name} and creates the docker-compose.yml file 
        using the template generator.

        """
        command = "mkdir -p {exec_path} && cd {exec_path} && echo \"{docker_compose}\" > docker-compose.yml".format(
            exec_path=self.exec_path, docker_compose=DockerComposeTemplate(server_name=self.server_name, game_name=self.game_name))

        _, stderr, _ = await run(command)
        
        if stderr:
            logger.error(
                f"Cannot create the docker compose file for the following server: {self.server_name}.")
            logger.debug(stderr)
            return False

        logger.info(
            f"Created docker compose file for the following server: {self.server_name}")
        return True

    async def remove(self) -> bool:
        """Delete the server

        Deletes the server entry from the data base, removes the container
        and renames the server folder with .trash-{servername}{date}

        """
        command = "cd {exec_path} && docker compose down && docker compose rm && mv {exec_path} /servers/.trash-{fname}".format(
            exec_path=self.exec_path, fname=self.server_name + datetime.today().strftime("%Y-%m-%d"))

        _, stderr, process = await run(command)

        if stderr:
            logger.error(
                f"Cannot remove the following server: {self.server_name}.")
            logger.debug(stderr)
            return False

        logger.info(
            f"Removed the following server: {self.server_name}")
        return True

    async def execute(self, command: str, *args: str):
        """Executes a command from the LGSM CLI script

        Executes a command from the LinuxGSM CLI script by
        executing the following command inside the server's container: ./{game_name} {command} "{args}"

        """

        command = "docker exec -i {server_name} bash -c \"./{game_name} {command} '{args}' && exit $?\"".format(
            server_name=self.server_name,
            game_name=self.game_name,
            command=command,
            args=" ".join(args))

        stdout, _, process = await run(command)

        return {
            "returncode": process.returncode,
            "stdout": stdout
        }

    async def start(self) -> bool | int:
        """Start the server

        Starts the server's container and also sends "start" command
        to the LinuxGSM script.

        """

        command = f"cd {self.exec_path} && docker compose up -d"
        
        _, _, process = await run(command)

        if process.returncode == 0:
            result = await self.execute("start")
            return result.get("returncode")
        else:
            return False

    async def stop(self, stop_container: bool) -> int:
        """Stop the server

        Sends "stop" command to the LinuxGSM script.
        If stop_container is true then it also stops the server's container. 

        @param stop_container Whether to stop the server's container

        """

        result = await self.execute("stop")
        rc = result.get("returncode")

        if not stop_container:
            return rc

        command = f"cd {self.exec_path} && docker compose stop"

        _, _, process = await run(command)

        return process.returncode

    async def restart(self) -> int:
        """Restart the server

        Sends "restart" command to the LinuxGSM script.

        """

        result = await self.execute("restart")
        return result.get("returncode")

    async def is_installed(self):
        """Check if the server is installed

        Checks if the server's container is created

        """
        command = f"cd {self.exec_path} && docker compose ps --all | wc -l"

        stdout, stderr, _ = await run(command)

        try:
            container_amount = int(stdout)
        except:
            logger.error("Can't convert container_amount to int: ", stdout, stderr)
            return False
        else:
            return container_amount > 1  # Check if there is at least one container in that folder

    async def get_status(self) -> ServerStatusEnum:
        """Check the server's status

        Checks the server's status by checking if the tmux session
        is running.

        """

        if not await self.is_installed():
            return ServerStatusEnum.NOT_INSTALLED

        command = f"docker exec -i {self.server_name} bash -c 'tmux list-sessions -F {self.game_name} 2> /dev/null | grep -Exc \"^{self.game_name}\" && exit $?'"

        stdout, _, process = await run(command)

        if "Error response from daemon" in stdout:
            return ServerStatusEnum.STOPPED

        match(process.returncode):
            case 1:
                return ServerStatusEnum.STOPPED
            case 0:
                return ServerStatusEnum.STARTED

    def __get_details_model(self, details: dict):
        return ServerDetailsModel(
            ip_address=details.get("Internet IP"),
        )

    async def get_details(self) -> ServerDetailsModel:
        """Get the server's details

        Executes the "details" command from the LinuxGSM script

        """
        result = await self.execute("details")
        if result.get("returncode") == ServerCommandsResponse.OK:
            details = ServerDetailsParser(result.get("stdout"))
            return self.__get_details_model(details)
        else:
            return ServerDetailsModel(
                ip_address=None,
            )

    def get_console_path(self):
        """Get the console logs file path

        """

        return f"{self.exec_path}/log/console/{self.game_name}-console.log"

    def get_console_stream(self, request, limit: int):
        """Get the console stream

        Returns a stream to read real-time content of the console logs file
        """

        return ConsoleStream(self, request, limit)

    async def execute_game_command(self, command: str) -> int:
        """Executes a command inside the server's console

        Executes the "send" LinuxGSM script command

        @param command The command that will be sent to the server

        """

        if await self.get_status() != ServerStatusEnum.STARTED:
            return ServerCommandsResponse.NOT_RUNNING

        regex = re.compile("[\"']")
        command = regex.sub('\\"',command)

        cmd = f"docker exec -i {self.server_name} bash -c 'tmux send-keys -t \"{self.game_name}\" \"{command}\" ENTER && exit $?'"

        stdout, _, _ = await run(cmd)

        if "no server running" in stdout:
            return ServerCommandsResponse.NOT_RUNNING
        return ServerCommandsResponse.OK

    async def get_details_model(self):
        details = await self.get_details()
        return ServerWithDetailsModel(
            game_name=self.game_name,
            server_name=self.server_name,
            server_pretty_name=self.server_pretty_name,
            server_status=await self.get_status(),
            details=details,
        )

    async def get_model(self):
        return ServerModel(
            server_name=self.server_name,
            server_pretty_name=self.server_pretty_name,
            game_name=self.game_name,
            server_status=await self.get_status()
        )
