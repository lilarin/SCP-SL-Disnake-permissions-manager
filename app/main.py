import asyncio
import json
from functools import wraps
import disnake
from disnake.ext import commands

from utils.time import Time
from utils.responses import Response
from utils.steam import SteamAPI
from utils.file_operations import FileOperations as Operation
from utils.file_manager import FileManager as File


with open("config.json", "r") as config_file:
    config = json.load(config_file)

bot = commands.InteractionBot(intents=None)


@bot.event
async def on_ready():
    print(f"[{await Time.get_normalised()}] Виконано вхід як {bot.user}")
    await asyncio.sleep(1)
    await bot.change_presence(
        activity=disnake.Activity(
            type=disnake.ActivityType.watching, name="на адміністрацію"
        )
    )


@bot.event
async def on_slash_command(inter):
    user = inter.author
    command = inter.data.name
    print(
        f"[{await Time.get_normalised()}] "
        f"Користувач {user} використав команду /{command}"
    )


@bot.event
async def on_slash_command_error(inter, error):
    if isinstance(error, commands.MissingAnyRole):
        allowed_roles = [
            role.mention
            for role_id in config.get("allowed_roles", [])
            if (role := inter.guild.get_role(role_id))
        ]

        if allowed_roles:
            roles_list = ", ".join(allowed_roles)
            await Response.send_ephemeral(
                inter,
                "Для використання цієї команди необхідно"
                f" мати одну з наступних ролей: \n{roles_list}"
            )
        else:
            await Response.send_ephemeral(
                inter,
                "На сервері немає ролей, яким дозволено використання бота"
            )
    else:
        print("Виникла непередбачувана помилка: ", error)


def check_channel():
    """
    Decorator to check the channel in which the command is used.
    Checks that the command is used in an authorized channel.
    If the command is used in the wrong channel, sends a link to the channel.
    """
    def check_channel_decorator(func):
        @wraps(func)
        async def wrapper(interaction, *args, **kwargs):
            allowed_channel_id = config["perms_channel_id"]
            if interaction.channel_id != allowed_channel_id:
                channel = await bot.fetch_channel(allowed_channel_id)
                message = (
                    "Цю команду не можна використовувати в цьому каналі\n"
                    f"Використовуйте канал {channel.mention}"
                )
                await Response.send_ephemeral(interaction, message)
                return
            await func(interaction, *args, **kwargs)
        return wrapper
    return check_channel_decorator


def check_steamid():
    """
    Decorator that checks if the SteamID passed in the command arguments is correct.
    If SteamID is incorrect, sends an error message to the user.
    If SteamID is correct, clears it of unnecessary characters.
    """
    def check_steamid_decorator(func):
        @wraps(func)
        async def wrapper(interaction, *args, **kwargs):
            steamid = kwargs["steamid"]
            steamid64 = await SteamAPI.clean_steamid64(steamid)
            if not steamid64:
                await Response.send_ephemeral(
                    interaction, "SteamID64 вказано невірно"
                )
                return
            kwargs.pop("steamid")
            kwargs["steamid"] = steamid64
            await func(interaction, *args, **kwargs)
        return wrapper
    return check_steamid_decorator


def check_role():
    """
    Decorator that checks if the role passed in the command arguments,
    is not in the list of forbidden roles. If the role is disallowed,
    sends an error message to the user.
    """
    def check_role_decorator(func):
        @wraps(func)
        async def wrapper(interaction, *args, **kwargs):
            role = kwargs["role"]
            if role in config["prohibited_roles_names"]:
                await Response.send_ephemeral(
                    interaction, "Цю роль заборонено видавати"
                )
                return
            await func(interaction, *args, **kwargs)
        return wrapper
    return check_role_decorator


@bot.slash_command(name="видати-роль", description="Видати роль на сервері")
@commands.has_any_role(*config["allowed_roles"])
@check_channel()
@check_steamid()
@check_role()
async def grant_role(
        interaction: disnake.ApplicationCommandInteraction,
        steamid: str = commands.Param(description="Введіть стім-айді людини"),
        role: str = commands.Param(description="Введіть роль"),
        server: str = commands.Param(
            choices=list(config["servers"].keys()), description="Оберіть сервер"
        ),
):
    await interaction.response.defer()
    profile_link = await SteamAPI.get_steam_profile_link(steamid)
    profile_name, profile_avatar = await SteamAPI.get_profile_name_and_avatar(steamid)

    await File.get(server, "ra_file")

    server_config = config["servers"][server]
    local_file_path = server_config["port"] + "-" + config["ra_file"]
    old_role = await Operation.get_role(steamid, local_file_path)

    if not await Operation.contains_role(role, local_file_path):
        await server_roles(interaction=interaction, server=server)
        return

    if old_role == role:
        await Response.send_silent(interaction, "Користувач вже має вказану роль")
        return
    elif old_role:
        await Operation.change_role(local_file_path, steamid, old_role, role)

        text = f"## [``{profile_name}``]({profile_link})\n"
        text += (
            f"### {server}\n Роль **``{role}``** була додана користувачу\n "
            f"Вона замінила стару роль **``{old_role}``**\n "
        )

        await Response.send(interaction, text, 0x36BE25, profile_avatar, True)

        await File.put(server, "ra_file")
        return
    else:
        await Operation.add_role(local_file_path, steamid, role)

        text = f"## [``{profile_name}``]({profile_link})\n"
        text += f"### {server}\n Роль **``{role}``** була додана користувачу\n "

        await Response.send(interaction, text, 0x36BE25, profile_avatar, True)

        await File.put(server, "ra_file")
        return


@bot.slash_command(name="забрати-роль", description="Забрати роль на сервері")
@commands.has_any_role(*config["allowed_roles"])
@check_channel()
@check_steamid()
async def remove_role(
        interaction: disnake.ApplicationCommandInteraction,
        steamid: str = commands.Param(description="Введіть стім-айді людини"),
        server: str = commands.Param(
            choices=list(config["servers"].keys()), description="Оберіть сервер"
        ),
):
    await interaction.response.defer()
    profile_link = await SteamAPI.get_steam_profile_link(steamid)
    profile_name, profile_avatar = await SteamAPI.get_profile_name_and_avatar(steamid)

    await File.get(server, "ra_file")

    server_config = config["servers"][server]
    local_file_path = server_config["port"] + "-" + config["ra_file"]
    old_role = await Operation.get_role(steamid, local_file_path)

    if not old_role:
        await Response.send_silent(interaction, "У користувача немає ролі на сервері")
        return
    else:
        await Operation.remove_role(local_file_path, steamid, old_role)

        text = f"## [``{profile_name}``]({profile_link})\n"
        text += f"### {server}\n Роль **``{old_role}``** була знята з користувача\n "

        await Response.send(interaction, text, 0xBE2536, profile_avatar, True)

        await File.put(server, "ra_file")
        return


async def update_server_data(server):
    await File.get(server, "ra_file")
    await File.get(server, "reserved_slots_file")
    await File.get(server, "whitelist_file")


@bot.slash_command(name="показати-користувача", description="Детальна інформація про користувача")
@commands.has_any_role(*config["allowed_roles"])
@check_channel()
@check_steamid()
async def show_user(
        interaction: disnake.ApplicationCommandInteraction,
        steamid: str = commands.Param(description="Введіть стім-айді людини"),
):
    response = disnake.Embed(description="Очікуйте...", color=0xFFFFFF)
    await interaction.response.send_message(embed=response, ephemeral=True)

    profile_link = await SteamAPI.get_steam_profile_link(steamid)
    profile_name, profile_avatar = await SteamAPI.get_profile_name_and_avatar(steamid)

    text = f"## [``{profile_name}``]({profile_link})\n"

    for server in config["servers"]:
        await update_server_data(server)
        server_config = config["servers"][server]
        local_file_path = server_config["port"] + "-" + config["ra_file"]
        role = await Operation.get_role(steamid, local_file_path)

        if role:
            text += f"### {server}\n Роль: **``{role}``** \n"
        else:
            text += f"### {server}\n Роль: **``немає``** \n"

        local_file_path = server_config["port"] + "-" + config["whitelist_file"]
        if await Operation.in_miscellaneous(local_file_path, steamid):
            text += "Білий список: ✅ "
        else:
            text += "Білий список: ❌ "

        local_file_path = server_config["port"] + "-" + config["reserved_slots_file"]
        if await Operation.in_miscellaneous(local_file_path, steamid):
            text += "Виділені слоти: ✅\n"
        else:
            text += "Виділені слоти: ❌\n"


    await Response.edit(interaction, text, profile_avatar)


@bot.slash_command(name="показати-користувачів", description="Інформація про користувачів серверу")
@commands.has_any_role(*config["allowed_roles"])
@check_channel()
async def show_users(
        interaction: disnake.ApplicationCommandInteraction,
        server: str = commands.Param(
            choices=list(config["servers"].keys()), description="Оберіть сервер"
        ),
        miscellaneous: str = commands.Param(
            choices=[
                disnake.OptionChoice(name="Білий список", value="whitelist"),
                disnake.OptionChoice(name="Виділені слоти", value="reserved_slots"),
            ],
            description="Відобразити білий список, або виділені слоти?",
            default=None,
        ),
):
    await Response.send_ephemeral(interaction, "Очікуйте...")

    text = f"## Користувачі {server} "
    users = []

    server_config = config["servers"][server]
    if not miscellaneous:
        await File.get(server, "ra_file")
        text += "\n(Адмін-права)\n"
        ra_file_path = server_config["port"] + "-" + config["ra_file"]

        count = 0
        data = await Operation.get_users(ra_file_path)

        for steamid64, user_role in data.items():
            profile_link = await SteamAPI.get_steam_profile_link(steamid64)
            profile_name = await SteamAPI.get_steam_profile_name(steamid64)
            count += 1
            user_data = (
                f"{count}. [``{profile_name}``]({profile_link}) – **{user_role}**"
            )
            users.append(user_data + "\n")
    else:
        if miscellaneous == "whitelist":
            await File.get(server, "whitelist_file")
            text += "\n(Білий список)\n"
            miscellaneous_file_path = (
                    server_config["port"] + "-" + config["whitelist_file"]
            )
        else:
            await File.get(server, "reserved_slots_file")
            text += "\n(Виділені слоти)\n"
            miscellaneous_file_path = (
                    server_config["port"] + "-" + config["reserved_slots_file"]
            )

        ids = await File.read(miscellaneous_file_path)
        for count, steamid64 in enumerate(set(ids.split("\n"))):
            if steamid64.startswith("#") or len(steamid64) < 17:
                continue
            profile_link = await SteamAPI.get_steam_profile_link(steamid64)
            profile_name = await SteamAPI.get_steam_profile_name(steamid64)
            user_data = f"{count}. [``{profile_name}``]({profile_link})"
            users.append(user_data + "\n")

    if not users:
        await Response.edit(interaction, "Користувачі з доступом відсутні")
        return

    united = text + "".join(users)
    if len(united) < 4000:
        await Response.edit(interaction, united)
    else:
        for user in users:
            segment = text + user
            if len(segment) < 4000:
                text += user
            else:
                if text:
                    await Response.edit(interaction, text)
                    text = user
                else:
                    await Response.send_ephemeral(interaction, text)
                    text = user
        if text != "":
            await Response.send_ephemeral(interaction, text)


@bot.slash_command(name="ролі-серверу", description="Показати ролі серверу")
@commands.has_any_role(*config["allowed_roles"])
@check_channel()
async def server_roles(
        interaction: disnake.ApplicationCommandInteraction,
        server: str = commands.Param(
            choices=list(config["servers"].keys()), description="Оберіть сервер"
        ),
):
    if "ролі-серверу" != interaction.data["name"]:
        text = "## Вказаної ролі немає на сервері\n"
        await Response.send_silent(interaction, "Очікуйте...")
    else:
        text = ""
        await Response.send_ephemeral(interaction, "Очікуйте...")

    await File.get(server, "ra_file")
    server_config = config["servers"][server]
    local_file_path = server_config["port"] + "-" + config["ra_file"]
    text += (
        f"### Ролі серверу {server}:\n "
        f"{await Operation.get_roles(local_file_path)}"
    )

    await Response.edit(interaction, text)


@bot.slash_command(name="білий-список", description="Керування білим списком")
@commands.has_any_role(*config["allowed_roles"])
@check_channel()
@check_steamid()
async def white_list(
        interaction: disnake.ApplicationCommandInteraction,
        steamid: str = commands.Param(description="Введіть стім-айді людини"),
        action: str = commands.Param(
            choices=[
                disnake.OptionChoice(name="Додати", value="додати"),
                disnake.OptionChoice(name="Видалити", value="видалити"),
            ],
            description="Оберіть дію",
        ),
        server: str = commands.Param(
            choices=list(config["servers"].keys()), description="Оберіть сервер"
        ),
):
    await interaction.response.defer()
    profile_link = await SteamAPI.get_steam_profile_link(steamid)
    profile_name, profile_avatar = await SteamAPI.get_profile_name_and_avatar(steamid)

    await File.get(server, "whitelist_file")

    server_config = config["servers"][server]
    local_file_path = server_config["port"] + "-" + config["whitelist_file"]

    if action == "додати":
        if await Operation.in_miscellaneous(local_file_path, steamid):
            await Response.send_silent(
                interaction, "Користувач вже доданий до білого списку серверу"
            )
            return
        else:
            await Operation.add_miscellaneous(local_file_path, steamid)
            text = f"## [``{profile_name}``]({profile_link})\n"
            text += f"### {server}\n Користувач доданий до білого списку серверу\n "

            await Response.send(interaction, text, 0x36BE25, profile_avatar, True)

            await File.put(server, "whitelist_file")
            return
    elif action == "видалити":
        if not await Operation.in_miscellaneous(local_file_path, steamid):
            await Response.send_silent(
                interaction, "Користувача немає у білому списку серверу"
            )
            return
        else:
            await Operation.remove_miscellaneous(local_file_path, steamid)
            text = f"## [``{profile_name}``]({profile_link})\n"
            text += f"### {server}\n Користувач видалений з білого списку серверу\n "

            await Response.send(interaction, text, 0xBE2536, profile_avatar, True)

            await File.put(server, "whitelist_file")
            return


@bot.slash_command(name="виділені-слоти", description="Керування виділеними слотами")
@commands.has_any_role(*config["allowed_roles"])
@check_channel()
@check_steamid()
async def reserved_slots(
        interaction: disnake.ApplicationCommandInteraction,
        steamid: str = commands.Param(description="Введіть стім-айді людини"),
        action: str = commands.Param(
            choices=[
                disnake.OptionChoice(name="Додати", value="додати"),
                disnake.OptionChoice(name="Видалити", value="видалити"),
            ],
            description="Оберіть дію",
        ),
        server: str = commands.Param(
            choices=list(config["servers"].keys()), description="Оберіть сервер"
        ),
):
    await interaction.response.defer()
    profile_link = await SteamAPI.get_steam_profile_link(steamid)
    profile_name, profile_avatar = await SteamAPI.get_profile_name_and_avatar(steamid)

    await File.get(server, "reserved_slots_file")

    server_config = config["servers"][server]
    local_file_path = server_config["port"] + "-" + config["reserved_slots_file"]

    if action == "додати":
        if await Operation.in_miscellaneous(local_file_path, steamid):
            await Response.send_silent(interaction, "Користувач вже має виділений слот")
            return
        else:
            await Operation.add_miscellaneous(local_file_path, steamid)
            text = f"## [``{profile_name}``]({profile_link})\n"
            text += f"### {server}\n Користувачу доданий виділений слот\n "

            await Response.send(interaction, text, 0x36BE25, profile_avatar, True)

            await File.put(server, "reserved_slots_file")
            return
    elif action == "видалити":
        if not await Operation.in_miscellaneous(local_file_path, steamid):
            await Response.send_silent(interaction, "Користувач не має виділеного слоту")
            return
        else:
            await Operation.remove_miscellaneous(local_file_path, steamid)
            text = f"## [``{profile_name}``]({profile_link})\n"
            text += f"### {server}\n Користувачу видалений виділений слот\n "
            await Response.send(interaction, text, 0xBE2536, profile_avatar, True)

            await File.put(server, "reserved_slots_file")
            return


bot.run(config["token"])
