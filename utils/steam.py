import asyncio
import aiohttp
import json
import re

from utils.time import Time


def load_api_key() -> str:
    with open("./config.json", "r") as config_file:
        config_data = json.load(config_file)
        return config_data.get("steam_api_key", "")


class SteamAPI:
    steam_api_key = load_api_key()

    @staticmethod
    async def get_url(steamid: str) -> str:
        return (
            f"https://api.steampowered.com/"
            f"ISteamUser/GetPlayerSummaries/"
            f"v0002/?key={SteamAPI.steam_api_key}&steamids={steamid}"
        )

    @staticmethod
    async def fetch_data(url: str, repetition: int = 0) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429 and repetition < 5:
                    await asyncio.sleep(1)
                    repetition += 1
                    return await SteamAPI.fetch_data(url, repetition)
                else:
                    print(
                        f"[{await Time.get_normalised()}] "
                        f"Error SteamAPI: {response.status}"
                    )
                    return {}

    @staticmethod
    async def get_profile_name_and_avatar(steamid: str) -> tuple:
        url = await SteamAPI.get_url(steamid)
        data = await SteamAPI.fetch_data(url)
        players = data.get("response", {}).get("players", [])
        if players:
            return (
                players[0].get("personaname", "Unknown"),
                players[0].get("avatarfull", "Unknown")
            )
        return steamid, None

    @staticmethod
    async def get_steam_profile_name(steamid: str) -> str:
        url = await SteamAPI.get_url(steamid)
        data = await SteamAPI.fetch_data(url)
        player = data.get("response", {}).get("players", [])[0]
        if player:
            return player.get("personaname", "Unknown")
        return steamid

    @staticmethod
    async def get_steam_profile_link(steamid: str) -> str:
        return f"https://steamcommunity.com/profiles/{steamid}"

    @staticmethod
    async def clean_steamid64(steamid: str) -> str | None:
        cleaned = re.sub(r"\D", "", steamid)
        if len(cleaned) == 17 and cleaned.isdigit():
            return cleaned
        return None
