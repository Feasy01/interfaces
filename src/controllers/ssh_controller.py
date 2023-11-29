from src.controllers.base_controller import BaseController
from src.interface.base_interface import Settings
from src.interface.ssh import SSH,SSHSettings
from paramiko import SSHClient, AutoAddPolicy
import asyncio
class SSHController(BaseController,SSH):
    def __init__(self):
        super().__init__()
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
    def register_device(self, interface_name:str, settings:Settings):
        super().register_device(interface_name,settings)
        self.open_connection(device=interface_name)
    def open_connection(self,device):
        self.client.connect(hostname=self.settings[device].hostname,username=self.settings[device].username,password=self.settings[device].password)

    async def send_command(self, command: str) -> None:
        ssh_stdin, ssh_stdout, ssh_stderr = self.client.exec_command(command)
        return(ssh_stdin, ssh_stdout, ssh_stderr)