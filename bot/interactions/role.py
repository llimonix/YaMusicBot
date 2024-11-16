from discord.ext import commands
from discord import option, Role, ApplicationContext, guild_only

from bot.utils.database import db


class SetRoleCommand(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="setrole",
        name_localizations={"ru": "set-role"},
        description="The role to which the bot will respond",
        description_localizations={"ru": "Роль на которую будет отвечать бот"},
    )
    @option(
        name="role",
        name_localizations={"ru": "роль"},
        description="The role to which the bot will respond",
        description_localizations={"ru": "Роль на которую будет отвечать бот"},
    )
    @guild_only()
    async def setrole(self, ctx: ApplicationContext, role: Role):
        member = ctx.guild.get_member(ctx.user.id)
        if member is None or not member.guild_permissions.manage_guild:
            return await ctx.respond(
                content="У вас нет прав для выполнения этой команды. Необходимо иметь право 'Управление сервером'",
                ephemeral=True,
            )

        guild_id = ctx.guild_id  # ID сервера
        role_id = role.id  # ID роли на сервере

        if not await db.server_exists(guild_id):
            await db.insert_role(guild_id, role_id)
        else:
            await db.update_role(guild_id, role_id)

        await ctx.respond(content=f"Установлена роль для управления ботом: {role.mention}", ephemeral=True)


def setup(bot):
    bot.add_cog(SetRoleCommand(bot))
