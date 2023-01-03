from models.ServerModel import ServerModel
import subprocess
from datetime import datetime
from services.utils import DockerComposeTemplate


class Server:
    def __init__(self, server_name: str, game_name: str):
        self.server_name = server_name
        self.game_name = game_name
        self.exec_path = "/servers/"+server_name

    def download(self):
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

    def install(self):
        command = "cd {} && docker compose up -d".format(self.exec_path)
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

    def remove(self):
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
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                output_stripped = output.strip().decode()
                print(output_stripped)
        rc = process.poll()
        return rc

    def start(self):
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
            return self.execute("start")
        else:
            return False

    def stop(self):
        rc = self.execute("stop")

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

    def restart(self):
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
            return self.execute("restart")
        else:
            return False

    def getModel(self):
        return ServerModel(
            server_name=self.server_name,
            game_name=self.game_name
        )
