import discord
from discord.ext import pages
import wavelink
from bot.utils.tools import sorted_queue, t_duration


class PaginatorHandler:
    def __init__(self, player: wavelink.Player):
        self.pages = []
        self.page_groups = []
        self.player = player
        self.all_length = ""
        self.load_pages()

    def get_embed(self, description):
        current_track = self.player.current
        description = (f"**♬ | Сейчас играет:** [{current_track.title}]({current_track.uri}) "
                       f"[<@{current_track.extras.requester_id}>]\n\n"
                       f"**Очередь треков:**\n{description}")

        embed = discord.Embed(
            color=discord.Color.from_rgb(0, 148, 255),
            description=description,
        ).add_field(
            name="Продолжительность",
            value=self.all_length,
            inline=True
        ).add_field(
            name="Всего треков",
            value=f"`{self.player.queue.count}`",
            inline=True
        )
        return embed

    def get_track_embed(self, tracks, heading):
        current_track = self.player.current
        msg = ""
        for i, track in enumerate(tracks, start=1):
            msg += f"**` {i} `** [{track['title']} - {track['author']}]({track['uri']}) [<@{track['requester_id']}>]\n"
        description = (f"**♬ | Сейчас играет:** [{current_track.title}]({current_track.uri}) "
                       f"[<@{current_track.extras.requester_id}>]\n\n"
                       f"**{heading}:**\n{msg}")

        embed = discord.Embed(
            color=discord.Color.from_rgb(0, 148, 255),
            description=description,
        ).add_field(
            name="Продолжительность",
            value=self.all_length,
            inline=True
        ).add_field(
            name="Всего треков",
            value=f"`{self.player.queue.count}`",
            inline=True
        )
        return embed

    def load_pages(self):
        queue, all_length = sorted_queue(self.player)
        self.all_length = t_duration(all_length)
        main_queue_msg = ""
        index = 1

        for i, (key, value) in enumerate(queue.items(), start=1):
            if value["type"] == "track":
                main_queue_msg += (f"**` {i} `** [{key} - {value['author']}]({value['uri']}) "
                                   f"[<@{value['requester_id']}>]\n")
            elif value["type"] in ["album", "playlist", "artist"]:
                type_search = {
                    'artist': "Плейлист",
                    'playlist': "Плейлист",
                    'album': "Альбом",
                }.get(value["type"], "Плейлист")
                main_queue_msg += (f"**` {i} `** {type_search}: {key} ({len(value['tracks'])} треков) "
                                   f"[<@{value['tracks'][0]['requester_id']}>]\n")
                track_pages = [
                    self.get_track_embed(tracks=value["tracks"][j:j + 10],
                                         heading=f"{type_search}: {key} ({len(value['tracks'])} треков)")
                    for j in range(0, len(value["tracks"]), 10)
                ]
                self.page_groups.append(pages.PageGroup(
                    pages=track_pages,
                    label=f"{type_search}: {key}",
                    use_default_buttons=False
                ))

            if index == 10:
                self.pages.append(self.get_embed(main_queue_msg))
                main_queue_msg = ""
                index = 0

            index += 1

        if not queue:
            self.pages.append(self.get_embed("Пусто"))
        elif main_queue_msg:
            self.pages.append(self.get_embed(main_queue_msg))

        # Добавление основного списка очереди как первой группы страниц
        self.page_groups.insert(0, pages.PageGroup(
            pages=self.pages,
            label="Основной список очереди",
            use_default_buttons=False
        ))

    async def respond(self, ctx: discord.ApplicationContext):
        page_buttons = [
            pages.PaginatorButton(
                "first", label="<<", style=discord.ButtonStyle.green
            ),
            pages.PaginatorButton(
                "prev", label="<", style=discord.ButtonStyle.green,
                disabled=True if len(self.pages) == 1 else False
            ),
            pages.PaginatorButton(
                "page_indicator", style=discord.ButtonStyle.gray, disabled=True, label="|"
            ),
            pages.PaginatorButton(
                "next", label=">", style=discord.ButtonStyle.green,
                disabled=True if len(self.pages) == 1 else False
            ),
            pages.PaginatorButton(
                "last", label=">>", style=discord.ButtonStyle.green
            ),
        ]

        paginator = pages.Paginator(
            pages=self.page_groups,
            show_menu=True,
            use_default_buttons=False,
            custom_buttons=page_buttons,
            menu_placeholder="Список треков плейлиста или альбома",
            timeout=600,
            disable_on_timeout=True
        )

        await paginator.respond(ctx, ephemeral=True)
