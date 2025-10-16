from discord import app_commands
import discord

def setup_new_schedule_command(bot, guild_id):
    @bot.tree.command(name="new_schedule", description="upload a new schedule", guild=guild_id)
    @app_commands.describe(schedule="Image of Schedule Document")
    async def newScheduleCommand(interaction: discord.Interaction, schedule: discord.Attachment):
        """Handle Upload Schedules"""

        if not schedule.content_type.startswith('image/'):
            await interaction.response.send_message("Please attach a valid schedule image file.", ephemeral=True)
            return
        
        await bot._process_image_attachment(scheduleImage=schedule, interaction=interaction)
        return