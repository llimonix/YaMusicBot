import logging

from bot.utils.mc_gen import MusicCard

import wavelink

import discord
from discord import Embed
from discord.ext import commands, tasks

from bot.ui import MediaPlayer
from bot.utils.tools import t_duration, delete_message_player, send_message_player, EmojiStr as ES
from bot.utils.sheduler import BOT_SCHEDULER, no_members_voice_channel
from bot.env import load_config


class WaveEvents(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.config = load_config()
        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()
        nodes = [wavelink.Node(uri=f"{self.config.HOST_WAVELINK}:{self.config.PORT_WAVELINK}",
                               password=self.config.PASS_WAVELINK, inactive_player_timeout=300)]
        if hasattr(self.bot, "node_connected") is False:
            await wavelink.Pool.connect(nodes=nodes, client=self.bot)
            self.bot.node_connected = True

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        logging.info(f"Wavelink запущен: {payload.node!r} | Возобновленных: {payload.resumed}")
        # BOT_SCHEDULER.add_job(no_members_voice_channel, id="no_members", trigger="interval", seconds=10,
        #                       replace_existing=True)
        await self.player_loop.start(node=payload.node)

    @tasks.loop(minutes=5)
    async def player_loop(self, node: wavelink.Node) -> None:
        try:
            total_channels = len(await node.fetch_players())
            msg_status = f"в {total_channels} каналах"
        except:
            msg_status = "/play | /help"

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=msg_status,
            )
        )

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            return

        if getattr(player, "is_looping", False):
            await player.play(player.queue.history[-1])
            return

        if not player.queue:
            if hasattr(player, "message"):
                try:
                    await player.message.delete()
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    pass
            return

        channel = self.bot.get_channel(player.interaction.channel.id) if hasattr(player, "interaction") else None
        if not channel:
            return

        try:
            message = await channel.fetch_message(player.message.id) if hasattr(player, "message") else None
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            message = None

        media_player, embed, file = await self.ui_player(player)

        if not message:
            player.message = await player.interaction.channel.send(embeds=embed, view=media_player, file=file)
        else:
            await message.edit(embeds=embed, view=media_player, file=file)

        await player.play(player.queue.get())

    @commands.Cog.listener()
    async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
        await send_message_player(player, title="Бот отключен от голосового чата!",
                                  description="Бот отключен из-за отсутствия активности!")
        await delete_message_player(player)
        await player.disconnect()

    @staticmethod
    async def ui_player(player: wavelink.Player) -> tuple[MediaPlayer, list[Embed], discord.File]:
        media_player = MediaPlayer()
        track: wavelink.Playable = player.queue[0]
        mscard = MusicCard(image_link=track.artwork, title=track.title, artists=track.author,
                           duration=t_duration(track.length), added_by=track.extras.requester_name)
        result, dominant_color = await mscard.create_music_card()
        r, g, b = dominant_color
        playlist_msg = f"[{track.playlist.name}]({track.playlist.url})" if track.playlist else "Нет"
        embed: Embed = discord.Embed(
            description=
            f"{ES.e_music}` [{t_duration(track.length)}] `[`{track.title} - {track.author}`]({track.uri})\n\n"
            f"> {ES.e_share} **Плейлист:** {playlist_msg}\n"
            f"> {ES.e_tracklist} **В очереди:** {len(player.queue) - 1} трек(ов)\n"
            f"> {ES.e_eject} **Добавил:** <@{track.extras.requester_id}>",
            color=discord.Color.from_rgb(r=r, g=g, b=b)
        )
        embed.set_author(name="Music Player", icon_url="https://i.imgur.com/noUMXgY.gif")
        embed.set_image(url=f"attachment://{result.filename}")

        embed2 = discord.Embed(color=discord.Color.from_rgb(r=r, g=g, b=b))
        embed2.set_image(url="https://i.imgur.com/j8iRvAS.png")

        return media_player, [embed, embed2], result


def setup(bot):
    bot.add_cog(WaveEvents(bot))
