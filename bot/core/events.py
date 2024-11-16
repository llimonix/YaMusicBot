import discord
from discord.ext import commands
from ..utils.database import db
import logging


class Events(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    async def send_dm_message(self, user_id, message):
        user = await self.bot.fetch_user(user_id)
        if user is not None:
            try:
                await user.send(message)
            except discord.Forbidden:
                logging.error(f"Не удалось отправить личное сообщение пользователю {user.name}")
        else:
            logging.error(f"Пользователь с ID {user_id} не найден")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            bot_member = await guild.fetch_member(self.bot.user.id)
            first_text_channel = next(
                (channel for channel in guild.text_channels if channel.permissions_for(bot_member).send_messages), None
            )
            channel_id = first_text_channel.id
        except:
            first_text_channel = None
            channel_id = 0

        server_exists = await db.server_exists(guild.id)
        if not server_exists:
            await db.insert_server(guild.id, channel_id)

        if first_text_channel is not None:
            embed = discord.Embed(color=0x2F3136)
            embed.set_image(
                url="https://message.style/cdn/images/03a15547e35e0a93692b4394a5cb567dd2469d12fdccad47a89bb262bcab9ee2.png"
            )
            embed2 = discord.Embed(
                title="Информация",
                description="> YaMusic - **активно разрабатывающийся** бот для Discord, \n> который позволяет слушать музыку из сервиса \n> **Яндекс.Музыка**. Он принимает ссылки на **треки, альбомы, \n> плейлисты, подкасты и книги**, а также распознает **\n> текстовые запросы**. Бот умеет  **перемешивать треки** в \n> очереди, чтобы  один и тот же плейлист или альбом звучал \n> по новому и не  надоедал вам. Так же бот умеет находить \n> **похожие треки** на  трек играющий в данный момент.  В \n> скором времени мы добавим функцию  **бесконечного \n> потока проигрывания музыки** с возможность \n> выбрать жанр.",
                colour=0x2F3136,
            )

            embed2.add_field(
                name="Поддержка",
                value="Чтобы бот стал ещё лучше, мы создали Discord сервер, где \nможно **задать вопрос**, **предложить идею** или **зарепортить \nбаг / недочёт**. Но там так же можно просто послушать \nмузыку или пообщаться с участниками. Сервер доступен \nпо [ссылке](https://discord.gg/pJYKXx3eBh).",
                inline=False,
            )
            embed2.add_field(
                name="Примечание",
                value="Чтобы начать пользоваться ботом напишите </play:1171295728300212344> \nили </help:1171295728300212345>",
                inline=False,
            )
            embeds = [embed, embed2]

            try:
                await first_text_channel.send(embeds=embeds)
                await Events.send_dm_message(
                    self,
                    348420809389506562,
                    f"Бот добавлен на сервер {guild.name} (ID: {guild.id}), первый текстовый канал: {first_text_channel.name} (ID: {channel_id})",
                )
            except:
                await Events.send_dm_message(
                    self, 348420809389506562, f"Бот добавлен на сервер {guild.name} (ID: {guild.id})"
                )
        else:
            await Events.send_dm_message(
                self, 348420809389506562, f"Бот добавлен на сервер {guild.name} (ID: {guild.id})"
            )


def setup(bot):
    bot.add_cog(Events(bot))
