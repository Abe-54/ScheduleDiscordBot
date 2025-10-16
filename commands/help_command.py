from discord import Interaction

def setup_help_command(bot, guild_id):
    @bot.tree.command(name="help", description="show all available commands", guild=guild_id)
    async def help_command(interaction: Interaction):
        help_text = """
        📋 **Schedule Bot Commands**
        `/help` - Show help
        `/new_schedule`
        `/schedule <employee_name>`
        `/sync_calendar <employee_name>`
        """
        await interaction.response.send_message(help_text)