import discord
from discord_bot import DiscordBot
from calendar_auth import test_calendar_connection, get_credentials
import os
from dotenv import load_dotenv
from discord import app_commands

load_dotenv()

def main():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = DiscordBot(command_prefix="!", intents=intents)

    GUILD_ID = discord.Object(int(os.getenv('DEV_GUILD_ID')))

    #Commands
    @bot.tree.command(name="help", description="show all available commands", guild=GUILD_ID)
    async def helpCommand(interaction: discord.Interaction):
        """Show available commands."""
        help_text = """
        📋 **Schedule Bot Commands**

        `!help` - Show this help message
        `!new schedule`
        `!schedule <employee_name>` - Show an employee's schedule
        `!schedule` - List all employees

        **Examples:**
        • `!schedule John Doe`
        • `!schedule`

        💡 **Tip:** Upload a schedule image first to load data!
        """
        await interaction.response.send_message(help_text) 
    
    @bot.tree.command(name="schedule", description="Show schedule for an employee", guild=GUILD_ID)
    @app_commands.describe(employee="The employee's name")
    async def scheduleCommand(interaction: discord.Interaction, employee: str):
        """Handle schedule queries."""

        if not bot.schedules:
            await interaction.response.send_message("❌ No schedule data loaded. Please upload a schedule image first by using the `/new_schedule` command!")
            return
        
        employee_schedule = _find_employee(bot, employee)
    
        if not employee_schedule:
            await interaction.response.send_message(f"❌ Employee '{employee}' not found.", ephemeral=True)
            return

        # Search for employee
        schedule_text = _format_employee_schedule(bot, employee_schedule['name'], employee_schedule['schedule'])
        await interaction.response.send_message(schedule_text)
    
    @bot.tree.command(name="new_schedule", description="upload a new schedule", guild=GUILD_ID)
    @app_commands.describe(schedule="Image of Schedule Document")
    async def newScheduleCommand(interaction: discord.Interaction, schedule: discord.Attachment):
        """Handle Upload Schedules"""

        if not schedule.content_type.startswith('image/'):
            await interaction.response.send_message("Please attach a valid schedule image file.", ephemeral=True)
            return
        
        await bot._process_image_attachment(scheduleImage=schedule, interaction=interaction)
        return
    
    @bot.tree.command(name="connect_to_google", description="Connect bot to Google Calendar", guild=GUILD_ID)
    async def connectToGoogleCommand(interaction: discord.Interaction):
        """Connect only *your* account to Google Calendar."""
        await interaction.response.send_message("🔄 Connecting to Google Calendar...")

        try:
            # Auth flow runs in console/browser
            calendars = test_calendar_connection()
            await interaction.followup.send(
                f"✅ Connected to Google! Available calendars: {', '.join(calendars)}"
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to connect: {e}")
    
    @bot.tree.command(name="sync_calendar", description="Sync an employee's schedule to your calendar", guild=GUILD_ID)
    @app_commands.describe(employee_name="The employee whose schedule you want to sync")
    async def syncCalendarCommand(interaction: discord.Interaction, employee_name: str):
        """Sync selected employee schedule to user's Google Calendar"""
        user_id = interaction.user.id

        # Find employee
        employee_schedule = _find_employee(bot, employee_name)
        if not employee_schedule:
            await interaction.response.send_message(f"❌ Employee '{employee_name}' not found!", ephemeral=True)
            return

        # Loop over days, add events
        from datetime import datetime
        results = []
        for day, times in employee_schedule["schedule"].items():
            if not times: 
                continue
            
            # Example: "09:00 AM - 05:00 PM"
            try:
                start_str, _, end_str = times.split(" ", 2)
                # Convert to real datetime (MVP: pick a sample week, parse with strptime)

                start_time = "2025-09-23T09:00:00-04:00"
                end_time   = "2025-09-23T17:00:00-04:00"

                link = add_event_to_calendar(user_id, f"{employee_name} shift", start_time, end_time)
                results.append(f"📅 {day}: synced -> {link}")
            except:
                results.append(f"⚠️ Could not sync {day}: {times}")

        await interaction.response.send_message("\n".join(results))

    bot.run(os.getenv('DISCORD_TOKEN'))

def _find_employee(bot, search_name: str) -> dict:
    """Find employee by name (case-insensitive, partial match)."""
    search_name = search_name.lower()
    
    for emp_name, schedule in bot.schedules.items():
        if search_name in emp_name.lower():
            return {"name": emp_name, "schedule": schedule}
    
    return None


def _format_employee_schedule(self, name: str, schedule: dict) -> str:
    """Format employee schedule for display."""
    week_info = f"**Week:** {self.current_week['From']} to {self.current_week['To']}" if self.current_week else ""
    
    schedule_lines = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for day in days:
        time_slot = schedule.get(day)
        if time_slot:
            schedule_lines.append(f"**{day}:** {time_slot}")
        else:
            schedule_lines.append(f"**{day}:** Off")
    
    return f"**{name}**\n" + "\n".join(schedule_lines)

if __name__ == "__main__":
    main()