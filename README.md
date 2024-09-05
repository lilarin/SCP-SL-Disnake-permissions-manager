# SCP:SL & Disnake Permissions Manager Bot

The goal of this project is to develop a convenient and easy-to-use bot for permissions management on SCP:SL game servers. The bot uses the Disnake library to provide a robust and flexible solution for managing server access and permissions directly from Discord. It simplifies server management tasks by offering an intuitive interface and a wide range of features.

## Set Up the Configuration File

You can use the `config.json.sample` file as an example structure for the configuration file. Below is a brief explanation of the fields:

- **token**: The Discord bot token, necessary for authenticating your bot with Discord. You can obtain it from the [Discord Developer Portal](https://discord.com/developers/applications).

- **address**: The SFTP server address where your SCP Secret Laboratory configuration files are stored. This is the remote server your bot will connect to for managing files.

- **port**: The port number used to connect to the SFTP server. This is typically `22` for standard SFTP connections but may vary depending on your server's setup.

- **password**: The password for the SFTP user account. This allows the bot to authenticate and access the remote files.

- **path**: The remote path to the directory containing your SCP Secret Laboratory configuration files. The bot will manage files in this directory.

- **ra_file**: The filename of the RemoteAdmin configuration file. This file contains administrator settings for your SCP Secret Laboratory server, such as roles, permissions, and users.

- **reserved_slots_file**: The filename of the reserved slots file. This file contains a list of user `steamid@steam` IDs.

- **whitelist_file**: The filename of the whitelist file. This file contains a list of user `steamid@steam` IDs.

- **perms_channel_id**: The Discord channel ID where the bot will only work. This should be a numeric ID representing a specific channel in your Discord server.

- **prohibited_roles_names**: A list of role names that are prohibited from being assigned to users by the bot. These roles should not be granted by the bot under any circumstances.

- **servers**: A dictionary containing server-specific configurations. Each key represents a server name, and the value is another dictionary with the following fields:
  - **username**: The SFTP username for the specific server. This might differ depending on whether you're connecting to a raw SFTP server or using a service like Pterodactyl.
  - **port**: The port number for the server (specific to that instance).

- **allowed_roles**: A list of Discord role IDs that are allowed to use specific bot commands. Only users with these roles will be able to use the bot.

- **steam_api_key**: An API key for accessing Steam services.

## Features

<details>
  <summary><b>Slash Commands for Role Management</b></summary>
  
  - **Grant Role (`/видати-роль`)**: Assign a specified role to a user on the server, ensuring the user doesn't already have the role and that the role exists on the server. If the user has a different role, the old role is replaced.
  - **Remove Role (`/забрати-роль`)**: Remove a role from a user on the server.
  - **Server Roles (`/ролі-серверу`)**: Show the roles available on the server.

</details>
<details>
  <summary><b>Whitelisting and Reserved Slots Management</b></summary>

  - **Whitelist Management**: Manage user access to the whitelist.
  - **Reserved Slots Management**: Manage user access to the reserved slots, ensuring that important users always have access to the server during high-traffic periods.

</details>
<details>
  <summary><b>Displaying Comprehensive Information About Users</b></summary>

  - **Show User (`/показати-користувача`)**: Retrieve detailed information about a user across all configured servers, including their roles, whitelisting status, and access to reserved slots.
  - **Show Users (`/показати-користувачів`)**: Display a list of users by admin access, whitelist access, or reserved slots on a server.

</details>
<details>
  <summary><b>Command Validation Using Decorators and Error Handling</b></summary>

  - **`check_channel()`**: Ensures that commands are used only in authorized channels. If a command is used in the wrong channel, a message is sent with the correct channel link.
  - **`check_steamid()`**: Validates the SteamID.
  - **`check_role()`**: Ensures that the role specified in the command is not in the list of prohibited roles. If it is, the command execution is halted, adding the ability to make some roles accessible only via manual change.

</details>
<details>
  <summary><b>Extra</b></summary>

  - **Asynchronous Handling**: All operations are performed asynchronously to ensure smooth bot performance.
  - **Steam Integration**: Commands can fetch and display a user's Steam profile link, name, and avatar.
  - **Server-Specific Configuration**: Each server's role, whitelist, and reserved slot settings are managed independently through a configuration file.

</details>

## Examples of usage

![image](https://imgur.com/cyV1L1e.png)
![image](https://imgur.com/xf76zZV.png)
![image](https://imgur.com/WlP1pJ6.png)
![image](https://imgur.com/DJnnX8r.png)
![image](https://imgur.com/D9CtDfu.png)
![image](https://imgur.com/YYvZ3uj.png)

## Requirements

* Python 3.10+ (3.12 recommended)
* Other requirements are located in `requirements.txt`

Use this command to install all necessary dependencies:
> `pip install -r requirements.txt`

## License

This project is licensed under the [Creative Commons BY-NC 4.0](LICENSE.md) License.
