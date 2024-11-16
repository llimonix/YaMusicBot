from discord import ui, ApplicationContext
import wavelink

from typing import cast


class VolumeModal(ui.Modal):
    def __init__(self, player: wavelink.Player):
        super().__init__(title="Изменить громкость")

        current_volume = player.volume

        self.volume = ui.InputText(
            label=f"Громкость | Текущая громкость: {current_volume}",
            placeholder="Введите значение от 0 до 100",
            max_length=3,
            min_length=1,
        )

        self.add_item(self.volume)

    async def callback(self, ctx: ApplicationContext):
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            return

        if ctx.user.voice is None or player.channel != ctx.user.voice.channel:
            await ctx.respond(
                content=f"Для этого действия вам нужно находиться в голосовом канале: {player.channel.mention}!",
                ephemeral=True,
            )
            return

        try:
            volume = int(self.volume.value)
            volume = max(min(volume, 100), 0)

            await player.set_volume(volume)

            await ctx.response.defer()
            await ctx.channel.send(
                content=f"{ctx.user.mention} установил громкость на {volume}%", delete_after=10, silent=True
            )

        except ValueError:
            await ctx.respond(content="Пожалуйста, введите корректное число от 0 до 100.", ephemeral=True)
