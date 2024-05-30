from typing import cast
import random

import wavelink

from discord import ui, ButtonStyle, Embed, Colour, ApplicationContext
from wavelink import LavalinkLoadException

from bot.ui.modal import VolumeModal
from bot.ui.paginator import PaginatorHandler
from bot.utils.tools import check_role, gen_id, EmojiStr as ES


class MediaPlayer(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(style=ButtonStyle.green, custom_id="play_or_pause", row=0, emoji=ES.e_pause)
    @check_role
    async def play_or_pause(self, button: ui.Button, ctx: ApplicationContext) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.message.delete()
            return

        if ctx.user.voice is None or player.channel != ctx.user.voice.channel:
            await ctx.respond(
                content=f"Для этого действия вам нужно находиться в голосовом канале: {player.channel.mention}!",
                ephemeral=True, delete_after=10
            )
            return

        media_player = MediaPlayer()

        player.is_looping = player.is_looping if hasattr(player, 'is_looping') else False

        for child in media_player.children:
            if isinstance(child, ui.Button) and child.custom_id == "play_or_pause":
                child.style = ButtonStyle.red if not player.paused else ButtonStyle.green
                child.emoji = ES.e_play if not player.paused else ES.e_pause
            if isinstance(child, ui.Button) and child.custom_id == "repeat_track":
                child.style = ButtonStyle.green if player.is_looping else ButtonStyle.gray

        await player.pause(not player.paused)
        await ctx.edit(view=media_player)
        await ctx.channel.send(
            content=f"{ctx.user.mention} {'ставит' if player.paused else 'снимает'} паузу!",
            delete_after=10, silent=True
        )

    @ui.button(style=ButtonStyle.red, custom_id="stop", row=0, emoji=ES.e_stop)
    @check_role
    async def stop(self, button: ui.Button, ctx: ApplicationContext) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.message.delete()
            return

        if ctx.user.voice is None or player.channel != ctx.user.voice.channel:
            await ctx.respond(
                content=f"Для этого действия вам нужно находиться в голосовом канале: {player.channel.mention}!",
                ephemeral=True, delete_after=10
            )
            return

        player.queue.clear()
        player.is_looping = False

        await player.stop(force=True)
        await ctx.channel.send(
            content=f"{ctx.user.mention} остановил музыку!",
            delete_after=10, silent=True
        )

    @ui.button(style=ButtonStyle.grey, custom_id="shuffle_tracks", row=1, emoji=ES.e_shuffle)
    @check_role
    async def shuffle_tracks(self, button: ui.Button, ctx: ApplicationContext) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.message.delete()
            return

        if ctx.user.voice is None or player.channel != ctx.user.voice.channel:
            await ctx.respond(
                content=f"Для этого действия вам нужно находиться в голосовом канале: {player.channel.mention}!",
                ephemeral=True, delete_after=10
            )
            return

        que = list(player.queue)
        playlist_uid = None
        tracks_item = []
        shuffled_queue = []

        for track in que:
            if track.extras.playlist_uid != playlist_uid:
                if tracks_item:
                    random.shuffle(tracks_item)
                    shuffled_queue.extend(tracks_item)
                    tracks_item = []

            tracks_item.append(track)
            playlist_uid = track.extras.playlist_uid

        if tracks_item:
            random.shuffle(tracks_item)
            shuffled_queue.extend(tracks_item)

        player.queue.clear()
        player.queue.put(shuffled_queue)

        await ctx.edit(view=self)
        await ctx.channel.send(
            content=f"{ctx.user.mention} перемешал все треки!",
            delete_after=10, silent=True
        )

    @ui.button(style=ButtonStyle.grey, custom_id="similars_tracks", row=1, emoji=ES.e_similar)
    @check_role
    async def similars_tracks(self, button: ui.Button, ctx: ApplicationContext) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.message.delete()
            return

        if ctx.user.voice is None or player.channel != ctx.user.voice.channel:
            await ctx.respond(
                content=f"Для этого действия вам нужно находиться в голосовом канале: {player.channel.mention}!",
                ephemeral=True, delete_after=10
            )
            return

        first_track = player.current.identifier

        try:
            tracks: wavelink.Search = await wavelink.Playable.search(first_track, source="ymrec")
        except LavalinkLoadException:
            await ctx.respond(
                embed=Embed(
                    title="Похожие треки",
                    description="Не удалось найти ни одного трека похожего на этот.",
                    color=Colour.red()
                ), ephemeral=True, delete_after=10
            )
            return

        if not tracks:
            await ctx.respond(
                embed=Embed(
                    title="Похожие треки",
                    description="Не удалось найти ни одного трека похожего на этот.",
                    color=Colour.red()
                ), ephemeral=True, delete_after=10
            )
            return

        playlist_uid = gen_id()

        if isinstance(tracks, wavelink.Playlist):
            tracks.extras = {"requester_id": ctx.user.id, "requester_name": ctx.user.display_name,
                             "playlist_uid": playlist_uid}
            await player.queue.put_wait(tracks)
        else:
            track = tracks[0]
            track.extras = {"requester_id": ctx.user.id, "requester_name": ctx.user.display_name,
                            "playlist_uid": playlist_uid}
            await player.queue.put_wait(track)

        await ctx.respond(
            embed=Embed(
                title="Похожие треки",
                description="Похожие треки были добавлены в очередь!",
                color=Colour.green()
            ), ephemeral=True, delete_after=10
        )

    @ui.button(style=ButtonStyle.blurple, custom_id="skip_track", row=0, emoji=ES.e_skip)
    @check_role
    async def skip_track(self, button: ui.Button, ctx: ApplicationContext) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.message.delete()
            return

        if ctx.user.voice is None or player.channel != ctx.user.voice.channel:
            await ctx.respond(
                content=f"Для этого действия вам нужно находиться в голосовом канале: {player.channel.mention}!",
                ephemeral=True, delete_after=10
            )
            return

        player.is_looping = False

        if player.paused:
            await player.pause(False)

        await ctx.channel.send(
            content=f"{ctx.user.mention} пропустил трек **{player.current.title}**!",
            delete_after=10, silent=True
        )
        await player.skip(force=True)
        await ctx.response.defer()

    @ui.button(style=ButtonStyle.blurple, custom_id="skip_playlist", row=0, emoji=ES.e_forward)
    @check_role
    async def skip_playlist(self, button: ui.Button, ctx: ApplicationContext) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.message.delete()
            return

        if ctx.user.voice is None or player.channel != ctx.user.voice.channel:
            await ctx.respond(
                content=f"Для этого действия вам нужно находиться в голосовом канале: {player.channel.mention}!",
                ephemeral=True, delete_after=10
            )
            return

        que = list(player.queue)

        playlist_uid = player.current.extras.playlist_uid
        tracks_to_delete = [track for track in que if track.extras.playlist_uid == playlist_uid]
        for track in tracks_to_delete:
            player.queue.remove(track)

        player.is_looping = False

        if player.paused:
            await player.pause(False)

        if player.current.playlist is None:
            msg = f"трек **{player.current.title}**"
        else:
            msg = f"плейлист **{player.current.playlist.name}**"

        await ctx.channel.send(
            delete_after=10,
            content=f"{ctx.user.mention} пропустил {msg}!", silent=True
        )
        await player.skip(force=True)
        await ctx.response.defer()

    @ui.button(style=ButtonStyle.grey, custom_id="repeat_track", row=0,
               emoji=ES.e_replay)
    @check_role
    async def repeat_track(self, button: ui.Button, ctx: ApplicationContext) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.message.delete()
            return

        if ctx.user.voice is None or player.channel != ctx.user.voice.channel:
            await ctx.respond(
                content=f"Для этого действия вам нужно находиться в голосовом канале: {player.channel.mention}!",
                ephemeral=True, delete_after=10
            )
            return

        media_player = MediaPlayer()
        player.is_looping = player.is_looping if hasattr(player, 'is_looping') else False

        for child in media_player.children:
            if isinstance(child, ui.Button) and child.custom_id == "repeat_track":
                child.style = ButtonStyle.green if not player.is_looping else ButtonStyle.gray
            if isinstance(child, ui.Button) and child.custom_id == "play_or_pause":
                child.style = ButtonStyle.red if player.paused else ButtonStyle.green
                child.emoji = ES.e_play if player.paused else ES.e_pause

        player.is_looping = False if player.is_looping else True

        await ctx.edit(view=media_player)
        await ctx.channel.send(
            content=f"{ctx.user.mention} {'включает' if player.is_looping else 'выключает'} повтор трека!",
            delete_after=10, silent=True
        )

    @ui.button(style=ButtonStyle.grey, custom_id="help", row=1, emoji=ES.e_help)
    async def help(self, button: ui.Button, ctx: ApplicationContext) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.message.delete()
            return

        embed = Embed(
            title="Подсказка",
            description=f"{ES.e_music} Данный бот проигрывает Треки/Альбомы/Плейлисты/Подкасты/Книги "
                        "из Яндекс.Музыки!\n\n"
                        "Вы можете добавить трек отправив ссылку/название трека или отрывок из песни с помощью "
                        "команды: </play:1171295728300212344>\n\n",
            colour=Colour.green(),
        )

        embed.add_field(
            name="Подсказки по кнопкам",
            value=f"{ES.e_pause} | {ES.e_play} - Паузка или продолжение проигрывания.\n"
                  f"{ES.e_skip} - Пропустить один Трек | Подкаст | Книгу в очереди.\n"
                  f"{ES.e_forward}- Пропустить целый плейлист в очереди.\n"
                  f"{ES.e_replay} - Повторять Трек | Подкаст | Книгу в очереди.\n"
                  f"{ES.e_shuffle} - Перемешать все треки во всех плейлистах.\n"
                  f"{ES.e_stop} - Полностью остановить проигрывание и очистить очередь!\n"
                  f"{ES.e_similar} - Добавить в очередь треки похожие на играющий.\n"
                  f"{ES.e_tracklist} - Очередь треков.\n"
                  f"{ES.e_volume} - Громкость проигрывания.\n"
        )

        await ctx.respond(
            embed=embed,
            ephemeral=True
        )

    @ui.button(style=ButtonStyle.grey, custom_id="queue", row=1, emoji=ES.e_tracklist)
    async def queue(self, button: ui.Button, ctx: ApplicationContext) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.message.delete()
            return

        if ctx.user.voice is None or player.channel != ctx.user.voice.channel:
            await ctx.respond(
                content=f"Для этого действия вам нужно находиться в голосовом канале: {player.channel.mention}!",
                ephemeral=True, delete_after=10
            )
            return

        pages = PaginatorHandler(player=player)

        await pages.respond(ctx)

    @ui.button(style=ButtonStyle.grey, custom_id="volume", row=1, emoji=ES.e_volume)
    @check_role
    async def volume(self, button: ui.Button, ctx: ApplicationContext) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.message.delete()
            return

        if ctx.user.voice is None or player.channel != ctx.user.voice.channel:
            await ctx.respond(
                content=f"Для этого действия вам нужно находиться в голосовом канале: {player.channel.mention}!",
                ephemeral=True, delete_after=10
            )
            return

        await ctx.response.send_modal(VolumeModal(player))
