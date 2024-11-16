import discord
from discord.ext import commands




class PrefixCommand(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.command(name="refresh", help="Обновить структуру бота")
    async def refresh(self, ctx):
        if ctx.author.id == 348420809389506562 and isinstance(ctx.channel, discord.DMChannel):
            cogs_list = [
                "interactions.play",
                "interactions.info",
                "interactions.help",
                "interactions.prefix",
                "interactions.role",
                "core.events",
                "core.wavelink.waveEvents",
            ]

            self.bot._pending_application_commands = []

            for cog in cogs_list:
                self.bot.reload_extension(f"bot.{cog}")

            synced = len(self.bot.all_commands) + len(self.bot.pending_application_commands)

            await self.bot.sync_commands(force=True)
            await ctx.channel.send(f"**Структура бота обновлена**\n" f"*Синхронизировано команд: {synced}*")


def setup(bot):
    bot.add_cog(PrefixCommand(bot))
