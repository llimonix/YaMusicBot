from typing import cast

import wavelink

from discord import ui, ButtonStyle, ApplicationContext
from discord.ext.commands import AutoShardedBot


async def test_view(bot: AutoShardedBot) -> ui.View:
    view = ui.View(timeout=None)
    view.bot = bot

    async def get_queue(btn: ui.Button, ctx: ApplicationContext) -> None:
        print(ctx, btn)
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            return

        await ctx.respond(btn.label)

    button_labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    button_callbacks = [lambda btn, ctx=ctx: get_queue(btn, ctx) for ctx in button_labels]

    for label, callback in zip(button_labels, button_callbacks):
        button = ui.Button(label=label, style=ButtonStyle.grey)
        button.callback = callback
        view.add_item(button)

    return view
