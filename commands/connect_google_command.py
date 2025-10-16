import discord
from calendar_api import test_calendar_connection


def setup_connect_google_command(bot, guild_id):
    @bot.tree.command(name="connect_to_google", description="Connect bot to Google Calendar", guild=guild_id)
    async def connectToGoogleCommand(interaction: discord.Interaction):
        """Connect only *your* account to Google Calendar."""
        await interaction.response.send_message("🔄 Connecting to Google Calendar...")

        is_connected = test_calendar_connection()

        if is_connected:
            await interaction.followup.send("✅ Successfully connected to Google Calendar!")
        else:
            await interaction.followup.send(
                "❌ Failed to connect to Google Calendar. Check logs for error details."
        )