from typing import cast

import discord
import wavelink
from wavelink.exceptions import LavalinkLoadException

from discord.ext import commands
from discord import (
    option,
    OptionChoice,
    ApplicationContext,
    Embed,
    Colour,
    ClientException,
    guild_only
)

from bot.ui import MediaPlayer
from bot.utils.database import db
from bot.utils.mc_gen import MusicCard
from bot.utils.tools import gen_id, t_duration, delete_message_player, EmojiStr as ES


class PlayCommand(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.slash_command(name="play", description="Add a song to the queue",
                            description_localizations={
                                "ru": "Добавить песню в очередь"
                            }
                            )
    @option(name="query", name_localizations={"ru": "ссылка-или-название"},
            description="Track Name/Playlist/Album/Podcast/Books or a link (Yandex.Music)!",
            description_localizations={
                "ru": "Название Трека/Плейлиста/Альбома/Подкаста/Книги или ссылка(Яндекс.Музыка)!"
            }
            )
    @option(name="modes", name_localizations={"ru": "режим"},
            description="queue mode",
            description_localizations={"ru": "режим добавления в очередь"},
            choices=[
                OptionChoice(name="Out of turn", value=1, name_localizations={"ru": "Вне очереди"}),
                OptionChoice(name="Normal mode", value=2, name_localizations={"ru": "Обычный режим"})
            ],
            required=False
            )
    @guild_only()
    async def play(self, ctx: ApplicationContext, *, query: str, modes: int = 2) -> None:
        """Воспроизведите песню с заданным запросом."""
        if not ctx.guild:
            return

        await ctx.respond(
            embed=Embed(
                title="Ожидайте...",
                color=Colour.yellow()
            ),
            ephemeral=True, delete_after=15
        )

        guild_id = ctx.guild_id  # ID сервера

        role_access = await db.select_role(guild_id)
        target_role = ctx.guild.get_role(role_access)

        if target_role is not None and role_access not in [role.id for role in ctx.user.roles]:
            await ctx.edit(
                embed=Embed(
                    title="Ошибка",
                    description=f"У вас нет роли {target_role.mention} для выполнения этого действия!",
                    color=Colour.red()
                ),
            )
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)

        if not player:
            try:
                voice_channel = ctx.user.voice.channel
                permissions = voice_channel.permissions_for(ctx.guild.me)
                if not permissions.connect or not permissions.speak:
                    await ctx.edit(
                        embed=Embed(
                            title="Ошибка",
                            description="У меня нет прав для подключения или говорить в этом голосовом канале.",
                            color=Colour.red()
                        ),
                    )
                    return
                player = await voice_channel.connect(cls=wavelink.Player)
            except AttributeError:
                await ctx.edit(
                    embed=Embed(
                        title="Ошибка",
                        description="Пожалуйста, сначала подключитесь к голосовому каналу, "
                                    "прежде чем использовать эту команду.",
                        color=Colour.red()
                    ),
                )
                return

            except ClientException:
                await ctx.edit(
                    embed=Embed(
                        title="Ошибка",
                        description="Мне не удалось подключиться к этому голосовому каналу. "
                                    "Пожалуйста, попробуйте снова.",
                        color=Colour.red()
                    ),
                )
                return
            except wavelink.exceptions.InvalidNodeException:
                await ctx.edit(
                    embed=Embed(
                        title="Ошибка",
                        description="Ошибка при попытке подключения к аудио-ноде. "
                                    "Пожалуйста, попробуйте еще раз позже.",
                        color=Colour.red()
                    ),
                )
                return
            except wavelink.exceptions.ChannelTimeoutException:
                await ctx.edit(
                    embed=Embed(
                        title="Ошибка",
                        description="Мне не удалось подключиться к этому голосовому каналу. "
                                    "Возможно у бота нет прав на подключение к данному голосовому каналу.",
                        color=Colour.red()
                    ),
                )

        player.autoplay = wavelink.AutoPlayMode.disabled

        if (ctx.user.voice is None or player.channel != ctx.user.voice.channel) and player.connected:
            await ctx.edit(
                embed=Embed(
                    title="Ошибка",
                    description=f"Вы можете воспроизводить песни только в {player.channel.mention}, "
                                "так как проигрыватель там уже запущен.",
                    color=Colour.red()
                ),
            )
            return

        try:
            tracks: wavelink.Search = await wavelink.Playable.search(query, source="ymsearch")
        except LavalinkLoadException:
            await ctx.edit(
                embed=Embed(
                    title="Ошибка",
                    description="Не удалось найти ни одного трека с этим запросом. Пожалуйста, попробуйте снова.",
                    color=Colour.red()
                ),
            )
            return

        if not tracks:
            await ctx.edit(
                embed=Embed(
                    title="Ошибка",
                    description="Не удалось найти ни одного трека с этим запросом. Пожалуйста, попробуйте снова.",
                    color=Colour.red()
                ),
            )
            return

        playlist_uid = gen_id()

        if isinstance(tracks, wavelink.Playlist):
            tracks.extras = {"requester_id": ctx.user.id, "requester_name": ctx.user.display_name,
                             "playlist_uid": playlist_uid}
            tracks_len = tracks.__len__()
            if modes == 2:
                await player.queue.put_wait(tracks)
            else:
                for track in tracks:
                    player.queue.put_at(0, track)

            type_search = {
                'artist': "Плейлист",
                'playlist': "Плейлист",
                'album': "Альбом",
            }.get(
                tracks.type, ""
            )
            await PlayCommand.add_to_queue_message(
                ctx=ctx,
                description=f"{type_search} **`{tracks.name}`** ({tracks_len})"
            )
        else:
            track = tracks[0]
            track.extras = {"requester_id": ctx.user.id, "requester_name": ctx.user.display_name,
                            "playlist_uid": playlist_uid}
            if modes == 2:
                await player.queue.put_wait(track)
            else:
                player.queue.put_at(0, track)

            await PlayCommand.add_to_queue_message(
                ctx=ctx,
                description=f"Трек **`{track}`**"
            )

        if not hasattr(player, "interaction"):
            player.interaction = ctx
        if not hasattr(player, "is_looping"):
            player.is_looping = False

        if not player.playing:
            await player.play(player.queue.get())
            await self.ui_player(ctx, player)

    @commands.slash_command(name="stop", description="Stop playing music or fix bot freezes",
                            description_localizations={
                                "ru": "Остановить проигрывание музыки или пофиксить зависание бота"
                            }
                            )
    @guild_only()
    async def stop(self, ctx: ApplicationContext) -> None:
        guild_id = ctx.guild_id  # ID сервера

        role_access = await db.select_role(guild_id)
        target_role = ctx.guild.get_role(role_access)

        if target_role is not None and role_access not in [role.id for role in ctx.user.roles]:
            await ctx.respond(
                embed=Embed(
                    title="Ошибка",
                    description=f"У вас нет роли {target_role.mention} для выполнения этого действия!",
                    color=Colour.red()
                ), delete_after=10, ephemeral=True
            )
            return

        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.respond(
                embed=Embed(
                    title="Ошибка",
                    description="Бот нигде не запущен!",
                    color=Colour.red()
                ), delete_after=10, ephemeral=True
            )
            return

        if ((ctx.user.voice is None or player.channel != ctx.user.voice.channel) and
                ctx.guild.get_member(self.bot.user.id).voice is not None):
            await ctx.respond(
                embed=Embed(
                    title="Ошибка",
                    description=f"Для этого действия вам нужно находиться в голосовом канале: "
                                f"{player.channel.mention}!",
                    color=Colour.red()
                ), delete_after=10, ephemeral=True
            )
            return

        await delete_message_player(player)

        await player.disconnect()
        await ctx.delete()
        await ctx.channel.send(
            content=f"{ctx.user.mention} остановил музыку!",
            delete_after=10, silent=True
        )

    @staticmethod
    async def add_to_queue_message(ctx: ApplicationContext, description: str) -> None:
        await ctx.edit(embed=Embed(
            colour=Colour.green(),
            description=f"{description} добавлен в очередь."
        ))
        await ctx.channel.send(
            content=f"{ctx.user.mention} добавил в очередь {description}!",
            delete_after=10, silent=True
        )

    @staticmethod
    async def ui_player(ctx: ApplicationContext, player: wavelink.Player) -> None:
        media_player = MediaPlayer()
        track: wavelink.Playable = player.current
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

        player.message = await ctx.channel.send(embeds=[embed, embed2], view=media_player, file=result)


def setup(bot):
    bot.add_cog(PlayCommand(bot))
