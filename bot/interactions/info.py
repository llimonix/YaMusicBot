from discord import (
    option,
    TextChannel,
    ApplicationContext,
    guild_only
)
from discord.ext import commands

from bot.utils.database import db


class SetInfoCommand(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.slash_command(name="setinfo", name_localizations={"ru": "set-info"},
                            description="The channel to which the bot will send information about new updates",
                            description_localizations={
                                "ru": "Канал, в который бот будет отправлять информацию о новых обновлениях"
                            }
                            )
    @option(name="channel", name_localizations={"ru": "канал"},
            description="Channel for updates",
            description_localizations={
                "ru": "Канал для обновлений"
            }
            )
    @guild_only()
    async def setinfo(self, ctx: ApplicationContext, channel: TextChannel):
        member = ctx.guild.get_member(ctx.user.id)
        if member is None or not member.guild_permissions.manage_guild:
            return await ctx.respond(
                content="У вас нет прав для выполнения этой команды. Необходимо иметь право 'Управление сервером'",
                ephemeral=True
            )

        guild_id = ctx.guild_id  # ID сервера
        info_id = channel.id  # ID текстового канала

        if not await db.server_exists(guild_id):
            await db.insert_info(guild_id, info_id)
        else:
            await db.update_info(guild_id, info_id)

        await ctx.respond(
            content=f"Установлен канал для уведомлений о обновлениях: {channel.mention}",
            ephemeral=True
        )


def setup(bot):
    bot.add_cog(SetInfoCommand(bot))
