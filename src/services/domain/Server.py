from models.ServerModel import ServerModel
import subprocess
from datetime import datetime


class Server:
    def __init__(self, server_name: str, game_name: str):
        self.server_name = server_name
        self.game_name = game_name
        self.exec_path = "/servers/"+server_name

    def download(self):
        command = "mkdir -p {} && cd {} && wget -O linuxgsm.sh https://linuxgsm.sh && chmod +x linuxgsm.sh && bash linuxgsm.sh {}".format(self.exec_path,self.exec_path,self.game_name)
        process = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE)

        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()

    def install(self):
        command = "cd {} && ./{} auto-install".format(self.exec_path,self.game_name)
        process = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                output_stripped = output.strip().decode()
                print(output_stripped)
        rc = process.poll()

    def remove(self):
        command = "mv {} /servers/.trash-{}".format(self.exec_path,self.server_name + datetime.today().strftime("%Y-%m-%d"))
        process = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                output_stripped = output.strip().decode()
                print(output_stripped)        
        rc = process.poll()

    def getModel(self):
        return ServerModel(
            server_name=self.server_name,
            game_name=self.game_name
        )
