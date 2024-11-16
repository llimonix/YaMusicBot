from discord import Colour, Embed, ApplicationContext
from discord.ext import commands


class HelpCommand(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="help",
        description="All existing bot commands",
        description_localizations={"ru": "Все существующие команды бота"},
    )
    async def help(self, ctx: ApplicationContext):
        embed = Embed(
            title="Помощь", description="Здесь описаны все существующие команды бота:", color=Colour.blurple()
        )
        embed.add_field(
            name="Музыка",
            value="</play:1171295728300212344> - проигрывание Трека/Альбома/Плейлиста/Подкаста/Книги из Яндекс.Музыки.\n\n"
            "Техническая поддержка: [Нажмите здесь](https://discord.gg/pJYKXx3eBh)\n"
            "Privacy Policy: [Нажмите здесь](https://llimonix.github.io/yandexmusic/privacy-policy)\n"
            "Terms of Service: [Нажмите здесь](https://llimonix.github.io/yandexmusic/terms-of-service)",
            inline=False,
        )

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(HelpCommand(bot))
