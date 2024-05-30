import asyncio

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands, pages


class PageTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pages = [
            "Page 1",
            [
                discord.Embed(title="Page 2, Embed 1"),
                discord.Embed(title="Page 2, Embed 2"),
            ],
            "Page Three",
            discord.Embed(title="Page Four"),
            discord.Embed(title="Page Five"),
            [
                discord.Embed(title="Page Six, Embed 1"),
                discord.Embed(title="Page Seven, Embed 2"),
            ],
        ]
        self.pages[3].set_image(
            url="https://c.tenor.com/pPKOYQpTO8AAAAAM/monkey-developer.gif"
        )
        self.pages[4].add_field(
            name="Example Field", value="Example Value", inline=False
        )
        self.pages[4].add_field(
            name="Another Example Field", value="Another Example Value", inline=False
        )

        self.more_pages = [
            "Second Page One",
            discord.Embed(title="Second Page Two"),
            discord.Embed(title="Second Page Three"),
        ]

        self.even_more_pages = ["11111", "22222", "33333"]

    def get_pages(self):
        return self.pages

    pagetest = SlashCommandGroup("pagetest", "Commands for testing ext.pages")

    @pagetest.command(name="custom_view")
    async def pagetest_custom_view(self, ctx: discord.ApplicationContext):
        """Demonstrates passing a custom view to the paginator."""
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Test Button, Does Nothing", row=1))
        view.add_item(
            discord.ui.Select(
                placeholder="Test Select Menu, Does Nothing",
                options=[
                    discord.SelectOption(
                        label="Example Option",
                        value="Example Value",
                        description="This menu does nothing!",
                    )
                ],
            )
        )
        paginator = pages.Paginator(pages=self.get_pages(), custom_view=view)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @pagetest.command(name="groups")
    async def pagetest_groups(self, ctx: discord.ApplicationContext):
        """Demonstrates using page groups to switch between different sets of pages."""
        page_buttons = [
            pages.PaginatorButton(
                "first", label="<<-", style=discord.ButtonStyle.green
            ),
            pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton(
                "page_indicator", style=discord.ButtonStyle.gray, disabled=True
            ),
            pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
            pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
        ]

        page_groups = [
            pages.PageGroup(
                pages=self.get_pages(),
                label="Основной список очереди",
                use_default_buttons=False
            ),
            pages.PageGroup(
                pages=[
                    "Second Set of Pages, Page 1",
                    "Second Set of Pages, Page 2",
                    "Look, it's group 2, page 3!",
                ],
                label="Я ебал собак",
                use_default_buttons=False
            ),
            pages.PageGroup(
                pages=[
                    "Second Set of Pages, Page 1",
                    "Second Set of Pages, Page 2",
                    "Look, it's group 2, page 3!",
                ],
                label="Я ебал собак",
                use_default_buttons=False
            ),
        ]

        paginator = pages.Paginator(pages=page_groups, show_menu=True, use_default_buttons=False,
                                    custom_buttons=page_buttons, menu_placeholder="Список треков плейлиста или альбома")
        await paginator.respond(ctx.interaction, ephemeral=False)


def setup(bot):
    bot.add_cog(PageTest(bot))