import re
import aiofiles

from utils.file_manager import FileManager


class FileOperations:
    @staticmethod
    async def get_role(steamid, filename) -> str | None:
        text = await FileManager.read(filename)
        for current in text.split("\n"):
            if steamid in current:
                return current.split(steamid + "@steam: ")[1].split("\\n")[0]
        return None

    @staticmethod
    async def get_roles(filename) -> str:
        text = await FileManager.read(filename)
        roles_section = text.split("Roles:")[1]
        return (
            roles_section.split("\n\n")[0]
            if "\n\n" in roles_section else roles_section
        )

    @staticmethod
    async def add_role(filename, steamid, role) -> None:
        text = await FileManager.read(filename)
        new_text = text.replace(
            "Members:\n",
            f"Members:\n - {steamid}@steam: {role}\n"
        )
        await FileManager.write(filename, new_text)

    @staticmethod
    async def get_users(filename) -> dict:
        steam_ids = {}
        async with aiofiles.open(filename, "r", encoding="utf-8") as file:
            async for line in file:
                match = re.search(r"(\d+@steam): (\w+)", line)
                if match:
                    steam_id, role = match.groups()
                    steam_ids[steam_id] = role
        return steam_ids

    @staticmethod
    async def change_role(filename, steamid, old_role, role):
        text = await FileManager.read(filename)
        new_text = text.replace(
            f"{steamid}@steam: {old_role}",
            f"{steamid}@steam: {role}"
        )
        await FileManager.write(filename, new_text)

    @staticmethod
    async def remove_role(filename, steamid, role):
        text = await FileManager.read(filename)
        new_text = text.replace(
            f" - {steamid}@steam: {role}\n",
            ""
        )
        await FileManager.write(filename, new_text)

    @staticmethod
    async def contains_role(role, filename):
        roles = await FileOperations.get_roles(filename)
        return any(
            f" - {role}" in line
            for line in roles.split("\n")
        )

    @staticmethod
    async def add_miscellaneous(filename, steamid):
        text = await FileManager.read(filename)
        new_text = text + f"\n{steamid}@steam"
        await FileManager.write(filename, new_text)

    @staticmethod
    async def remove_miscellaneous(filename, steamid):
        text = await FileManager.read(filename)
        new_text = text.replace(
            f"\n{steamid}@steam",
            ""
        )
        await FileManager.write(filename, new_text)

    @staticmethod
    async def in_miscellaneous(filename, steamid):
        text = await FileManager.read(filename)
        return steamid in text
