import disnake

from utils.time import Time


class Response:
    @staticmethod
    async def send(
            interaction,
            message,
            color = None,
            thumbnail = None,
            footer = False
    ) -> None:
        if color:
            response = disnake.Embed(
                description=message,
                color=color,
                timestamp=await Time.get_current()
            )
        else:
            response = disnake.Embed(description=message, color=0xFFFFFF)

        if thumbnail:
            response.set_thumbnail(url=thumbnail)
        if footer:
            response.set_footer(
                text=interaction.user.display_name,
                icon_url=interaction.user.avatar
            )

        await interaction.send(embed=response)

    @staticmethod
    async def send_silent(interaction, message):
        ephemeral_response = disnake.Embed(description=message, color=0xFFFFFF)
        await interaction.send(embed=ephemeral_response)
        await interaction.delete_original_response(delay=10)

    @staticmethod
    async def send_ephemeral(interaction, message) -> None:
        ephemeral_response = disnake.Embed(description=message, color=0xFFFFFF)
        await interaction.send(embed=ephemeral_response, ephemeral=True)

    @staticmethod
    async def edit(interaction, message, thumbnail = None) -> None:
        new_response = disnake.Embed(description=message, color=0xFFFFFF)

        if thumbnail:
            new_response.set_thumbnail(url=thumbnail)

        await interaction.edit_original_response(embed=new_response)
