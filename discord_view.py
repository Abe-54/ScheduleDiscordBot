import discord


class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success, emoji="✅")
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.edit_message(
            content="✅ You chose **Yes**.",
            view=None
        )

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger, emoji="❌")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.edit_message(
            content="❌ You chose **No**.",
            view=None
        )