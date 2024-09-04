import json

import aiofiles
import asyncssh
from asyncssh import SSHClientConnection

with open("./config.json", "r") as config_file:
    config = json.load(config_file)


class FileManager:
    @staticmethod
    async def _init_ssh_client(server) -> SSHClientConnection:
        server_config = config["servers"][server]
        sftp_host = config["address"]
        sftp_port = int(config["port"])
        sftp_password = config["password"]
        sftp_username = server_config["username"]

        ssh_client = await asyncssh.connect(
            sftp_host,
            port=sftp_port,
            username=sftp_username,
            password=sftp_password,
            known_hosts=None
        )
        return ssh_client

    @staticmethod
    async def _transfer_file(server, choose, action) -> None:
        server_config = config["servers"][server]

        local_file_path = server_config["port"] + "-" + config[choose]
        remote_file_path = config["path"] + server_config["port"] + "/" + config[choose]

        async with await FileManager._init_ssh_client(server) as ssh_client:
            async with ssh_client.start_sftp_client() as sftp:
                if action == "put":
                    async with aiofiles.open(local_file_path, "rb") as local_file:
                        file_data = await local_file.read()
                        async with sftp.open(remote_file_path, "wb") as remote_file:
                            await remote_file.write(file_data)
                elif action == "get":
                    async with sftp.open(remote_file_path, "rb") as remote_file:
                        file_data = await remote_file.read()
                        async with aiofiles.open(local_file_path, "wb") as local_file:
                            await local_file.write(file_data)

    @staticmethod
    async def put(server, choose) -> None:
        await FileManager._transfer_file(server, choose, "put")

    @staticmethod
    async def get(server, choose) -> None:
        await FileManager._transfer_file(server, choose, "get")

    @staticmethod
    async def read(filename) -> str:
        async with aiofiles.open(filename, "r", encoding="utf-8") as file:
            return await file.read()

    @staticmethod
    async def write(filename, content) -> None:
        async with aiofiles.open(filename, "w", encoding="utf-8") as file:
            await file.write(content)
