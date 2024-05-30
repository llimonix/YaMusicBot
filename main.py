import asyncio
import logging

import sys

import discord
from discord.ext import commands

from bot.ui import MediaPlayer
from bot.utils.database import db
from bot.utils.sheduler import BOT_SCHEDULER


class Bot(commands.AutoShardedBot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True

        logging.basicConfig(level=logging.INFO)
        logging.getLogger('apscheduler').setLevel(logging.WARNING)
        super().__init__(command_prefix="?", intents=intents, help_command=None)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Дождитесь полного запуска бота или синхронизации команд на сервере!")
        elif isinstance(error, discord.ApplicationCommandError):
            await ctx.send("Дождитесь полного запуска бота или синхронизации команд на сервере!")
        elif isinstance(error, discord.ApplicationCommandInvokeError):
            await ctx.send("Дождитесь полного запуска бота или синхронизации команд на сервере!")
        else:
            print(f'Unhandled error: {error}')

    async def on_ready(self) -> None:
        await db.create_table()
        bot.add_view(MediaPlayer())
        BOT_SCHEDULER.start()
        logging.info(f"Logged in: {self.user} | {self.user.id}")


bot: Bot = Bot()


async def main() -> None:
    async with bot:
        await load_extensions()
        await bot.start('MTA0NDcyMTI2NzgxMjYxMDI1MA.GwNI-a.lciZSrZcqt_TvT5E3U-uCmigE5lAVrZg0Wj6L4')
        #await bot.start('MTE3MTI5NDQwMzA3MjExODg1NA.Gb1TVG.3EFGR8CuaGSYTv-aYSTFYSW_Bi4MPrMo3uUO-0')


async def load_extensions() -> None:
    print("Loading extensions...")
    cogs_list = [
        'interactions.play',
        'interactions.help',
        'interactions.prefix',
        'interactions.role',
        'core.events',
        'core.wavelink.waveEvents',
    ]

    for cog in cogs_list:
        bot.load_extension(f'bot.{cog}')


loop = asyncio.get_event_loop()
loop.create_task(main())

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.stop()
    sys.exit(0)


