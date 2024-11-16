import random

import discord
import wavelink
from discord import Embed, Colour

from bot.utils.database import db


class EmojiStr:
    e_pause = "<:Pause:1184651775932899489>"
    e_play = "<:Play:1184651778193633301>"
    e_skip = "<:Skip:1184651781117071590>"
    e_forward = "<:forward:1184651770748735539>"
    e_replay = "<:Replay:1184651779800059914>"
    e_shuffle = "<:shuffle:1184653819213258773>"
    e_stop = "<:Stop:1184651783386169437>"
    e_similar = "<:similar:1184651771998634055>"
    e_tracklist = "<:Tracklist:1184651785227472947>"
    e_volume = "<:volume:1191867558572347424>"
    e_help = "<:help:1184651774267752478>"
    e_yamusic = "<:yamusic:1184659403195043921>"
    e_next = "<:next:1243754982994350160>"
    e_back = "<:_back:1243754981690179705>"
    e_music = "<:music:1243754986643656745>"
    e_eject = "<:_eject:1243754985548681217>"
    e_share = "<:share:1243754984210825259>"


# Стандартные функции
def split_author(author: str) -> str:
    elements = author.split(", ")

    new_text = ""
    for i, element in enumerate(elements):
        if i % 2 == 0 and i != 0:
            new_text += "\n"
        new_text += element
        if i != len(elements) - 1:
            new_text += ", "

    return new_text


def t_duration(length: int) -> str:
    minutes, seconds = divmod(length // 1000, 60)

    if minutes > 60:
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return f"{minutes:02d}:{seconds:02d}"


def gen_id(len_password: int = 16, type_password: str = "default") -> str:
    if type_password == "default":
        char_password = list("1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ")
    elif type_password == "letter":
        char_password = list("abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ")
    elif type_password == "number":
        char_password = list("1234567890")
    elif type_password == "onechar":
        char_password = list("1234567890")
    else:
        char_password = list("1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ")

    random.shuffle(char_password)
    random_chars = "".join([random.choice(char_password) for x in range(len_password)])

    if type_password == "onechar":
        random_chars = f"{random.choice('abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ')}{random_chars[1:]}"

    return random_chars


# Вспомогательные функции дискорда
def check_voice(func):
    async def wrapper(*args, **kwargs):
        if args[2].user.voice:
            return await func(*args)
        else:
            await args[2].response.send_message(
                "Для выполнения этого действия вы должны находится в голосовом канале!", ephemeral=True
            )

    return wrapper


def check_role(func):
    async def wrapper(*args, **kwargs):
        interaction = args[2]
        server_exists = await db.server_exists(interaction.guild_id)
        if not server_exists:
            await db.insert_server(interaction.guild_id, 0)
            return await func(*args)
        else:
            role_access = await db.select_role(interaction.guild_id)
            target_role = interaction.guild.get_role(role_access)

            if target_role is not None and role_access not in [role.id for role in interaction.user.roles]:
                embed = Embed(
                    title="Ошибка",
                    description=f"У вас нет роли {target_role.mention} для выполнения этого действия!",
                    color=Colour.red(),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                return await func(*args)

    return wrapper


async def delete_message_player(player: wavelink.Player):
    if hasattr(player, "message"):
        try:
            await player.message.delete()
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass


async def send_message_player(player: wavelink.Player, title: str, description: str):
    if hasattr(player, "interaction"):
        try:
            await player.interaction.channel.send(
                embed=discord.Embed(title=title, description=description, color=discord.Colour.brand_red()),
                delete_after=10,
            )
        except (discord.HTTPException, discord.Forbidden, discord.InvalidArgument):
            pass


def sorted_queue(player):
    que = list(player.queue)

    playlist_uid = None
    media_item_queue = []
    all_length = 0

    def add_tracks_to_queue(tracks):
        nonlocal all_length
        all_length += sum(track.length for track in tracks)
        return [
            {"title": track.title, "author": track.author, "uri": track.uri, "requester_id": track.extras.requester_id}
            for track in tracks
        ]

    for track in que:
        if track.extras.playlist_uid != playlist_uid:
            if media_item_queue and media_item_queue[-1]:
                media_item_queue[-1]["tracks"] = add_tracks_to_queue(media_item_queue[-1]["tracks"])
            media_item_queue.append({"playlist": track.playlist, "tracks": []})

        media_item_queue[-1]["tracks"].append(track)
        playlist_uid = track.extras.playlist_uid

    if media_item_queue and media_item_queue[-1]:
        media_item_queue[-1]["tracks"] = add_tracks_to_queue(media_item_queue[-1]["tracks"])

    queue_dict = {}
    for item in media_item_queue:
        if item["playlist"]:
            playlist_name = item["playlist"].name
            type_search = (
                item["playlist"].type if item["playlist"].type in ["album", "playlist", "artist"] else "playlist"
            )
            queue_dict[playlist_name] = {"type": type_search, "tracks": item["tracks"]}
        else:
            for track in item["tracks"]:
                queue_dict[track["title"]] = {
                    "type": "track",
                    "author": track["author"],
                    "uri": track["uri"],
                    "requester_id": track["requester_id"],
                }

    return queue_dict, all_length
