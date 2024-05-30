from typing import cast

import discord
import wavelink

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TIMEZONE = "Europe/Moscow"

jobstores = {
    'default': RedisJobStore(jobs_key='dispatched_trips_jobs',
                             run_times_key='dispatched_trips_running',
                             host='localhost',
                             port=6333,
                             db=1)
}

BOT_SCHEDULER = ContextSchedulerDecorator(AsyncIOScheduler(timezone=BOT_TIMEZONE, jobstores=jobstores))


async def no_members_voice_channel():
    async def disconnect_player(no_player: wavelink.Player):
        if not no_player:
            return

        channel = no_player.client.get_channel(no_player.interaction.channel.id) if hasattr(no_player, "interaction") else None
        if not channel:
            return

        try:
            message = await channel.fetch_message(no_player.message.id) if hasattr(no_player, "message") else None
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            message = None

        if message:
            await channel.send(
                embed=discord.Embed(
                    title="Информация",
                    description="Бот отключен из-за отсутствия активности!",
                    color=discord.Colour.orange()
                ),
                delete_after=10
            )
            await message.delete()

        await no_player.disconnect()

    for node in wavelink.Pool.nodes.values():
        players = await node.fetch_players()

        for _player in players:
            player = node.get_player(_player.guild_id)
            if player is not None and player.channel is not None:
                count = player.channel.members.__len__()
                if count == 1:
                    player.no_members = player.no_members + 10 if hasattr(player, 'no_members') else 10
                    if player.no_members >= 300:
                        await disconnect_player(player)
                else:
                    player.no_members = 0 if hasattr(player, 'no_members') else 0
