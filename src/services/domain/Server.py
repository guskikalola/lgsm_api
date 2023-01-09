from models import ServerModel
from models import ServerDetailsModel, ServerWithDetailsModel
import subprocess
from datetime import datetime
from services.utils import DockerComposeTemplate, ServerDetailsParser
from services.enums import ServerCommandsResponse
from services.utils import ConsoleStream


class Server:
    def __init__(self, server_name: str, game_name: str):
        self.server_name = server_name
        self.game_name = game_name
        self.exec_path = "/servers/"+server_name

    def download(self) -> int:
        command = "mkdir -p {exec_path} && cd {exec_path} && echo \"{docker_compose}\" > docker-compose.yml".format(
            exec_path=self.exec_path, docker_compose=DockerComposeTemplate(server_name=self.server_name, game_name=self.game_name))
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()
        return rc

    def remove(self) -> int:
        command = "cd {exec_path} && docker compose down && docker compose rm && mv {exec_path} /servers/.trash-{fname}".format(
            exec_path=self.exec_path, fname=self.server_name + datetime.today().strftime("%Y-%m-%d"))
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                output_stripped = output.strip().decode()
                print(output_stripped)
        rc = process.poll()
        return rc

    def execute(self, command: str, *args):
        command = "docker exec -i {server_name} bash -c \"./{game_name} {command} {args} && exit $?\"".format(
            server_name=self.server_name,
            game_name=self.game_name,
            command=command,
            args=" ".join(args))
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        stdout = ""
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                output_decoded = output.decode()
                stdout += output_decoded
        rc = process.poll()
        return {
            "returncode": rc,
            "stdout": stdout
        }

    def start(self) -> bool | int:
        command = f"cd {self.exec_path} && docker compose up -d"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                output_stripped = output.strip().decode()
                print(output_stripped)
        rc = process.poll()
        if rc == 0:
            return self.execute("start").get("returncode")
        else:
            return False

    def stop(self, stop_container: bool) -> int:
        rc = self.execute("stop").get("returncode")

        if not stop_container:
            return rc

        command = f"cd {self.exec_path} && docker compose stop"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                output_stripped = output.strip().decode()
                print(output_stripped)
        process.poll()
        return rc

    def restart(self) -> int:
        return self.execute("restart").get("returncode")

    def __get_details_model(self, details: dict):
        return ServerDetailsModel(
            ip_address=details.get("Internet IP"),
            status=details.get("Status")
        )

    def get_details(self) -> ServerDetailsModel:
        result = self.execute("details")
        if result.get("returncode") == ServerCommandsResponse.OK:
            details = ServerDetailsParser(result.get("stdout"))
            return self.__get_details_model(details)
        else:
            if self.installed():
                status = "STOPPED"
            else:
                status = "NOT INSTALLED"
            return ServerDetailsModel(
                ip_address=None,
                status=status
            )

    def get_console_path(self):
        return f"{self.exec_path}/log/console/{self.game_name}-console.log"

    async def get_console_stream(self, request):
        return ConsoleStream(self,request)

    def execute_game_command(self,command: str) -> int:
        result = self.execute("send",command)
        return result.get("returncode")

    def get_details_model(self):
        details = self.get_details()
        return ServerWithDetailsModel(
            game_name=self.game_name,
            server_name=self.server_name,
            details=details,
        )

    def get_model(self):
        return ServerModel(
            server_name=self.server_name,
            game_name=self.game_name
        )        

    def getModel(self) -> ServerModel:
        return self.get_model()

    def installed(self):
        command = f"cd {self.exec_path} && docker compose ps --all | wc -l"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        stdout = ""
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                output_decoded = output.decode()
                stdout += output_decoded
        process.poll()
        try:
            container_amount = int(stdout)
        except:
            print("Can't convert container_amount to int: ", stdout)
            return False
        else:
            return container_amount > 1 # Check if there is at least one container in that folder