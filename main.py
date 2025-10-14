import discord
import pytz
import os
from discord_bot import DiscordBot
from calendar_api import create_new_calendar, get_primary_calendar, test_calendar_connection, get_credentials, add_event_to_new_calendar
from datetime import datetime, timedelta
from dotenv import load_dotenv
from discord import app_commands
from discord_view import ConfirmView

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

        is_connected = test_calendar_connection()

        if is_connected:
            await interaction.followup.send("✅ Successfully connected to Google Calendar!")
        else:
            await interaction.followup.send(
                "❌ Failed to connect to Google Calendar. Check logs for error details."
        )
            
    @bot.tree.command(name="sync_calendar", description="Sync an employee's schedule to your calendar", guild=GUILD_ID)
    @app_commands.describe(employee_name="The employee whose schedule you want to sync")
    async def syncWorkCalendarCommand(interaction: discord.Interaction, employee_name: str):
        """Sync selected employee schedule to user's Google Calendar"""
        user_id = interaction.user.id

        if not hasattr(bot, "schedules") or not bot.schedules:
            await interaction.response.send_message(
                "❌ No schedule data loaded. Upload a schedule first!", ephemeral=True
            )
            return

        employee_schedule = _find_employee(bot, employee_name)
        if not employee_schedule:
            await interaction.response.send_message(
                f"❌ Employee '{employee_name}' not found!", ephemeral=True
            )
            return
        
        is_connected = test_calendar_connection()

        if not is_connected:
            await interaction.followup.send(
                "❌ Failed to connect to Google Calendar.", ephemeral=True
            )  
            return

        # Loop over days, add events
        results = []
        week_start = datetime.strptime(bot.current_week["From"], "%m/%d/%Y")

        # Ask the user if they want to use their primary calendar - Y/N
        view = ConfirmView()
        await interaction.response.send_message(
            "Would you like to use your **primary calendar**?",
            view=view,
            ephemeral=True,
        )

        await view.wait()  # Wait for user to click

        use_primary = view.value
        calendar_id = None
        calender_name = None

        if use_primary:
            calendar_id = 'primary'
            calender_name = get_primary_calendar().get("summary")
        else:
            new_calendar = create_new_calendar()

            calendar_id = new_calendar["id"]
            calender_name = new_calendar["summary"]

        await interaction.followup.send(f"⏳ Syncing events using {calender_name} ...", ephemeral=True)

        for day, times in employee_schedule["schedule"].items():
            if not times: 
                continue
            
            # Example: "09:00 AM - 05:00 PM"
            try:
                parts = times.split("-")
                start_str, end_str = parts[0].strip(), parts[1].strip()
                start_time = _combine_day_and_time(week_start, day, start_str)
                end_time   = _combine_day_and_time(week_start, day, end_str)

                event = add_event_to_new_calendar(
                    user_id, f"{employee_name} shift", start_time, end_time, calendar_id
                )
                link = event.get("htmlLink", "(no link)")
                results.append(f"✅ {day}: synced → {link}")
            except:
                results.append(f"⚠️ Could not sync {day}: {times}")

        await interaction.followup.send("\n".join(results))

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

def _combine_day_and_time(week_start, day_name, time_str):
    # Map weekday strings to offsets
    day_index = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].index(day_name)
    tz = pytz.timezone("America/New_York")

    # Trim things like "09:00 AM"
    t = datetime.strptime(time_str.strip(), "%I:%M %p").time()
    dt = datetime.combine(week_start + timedelta(days=day_index), t)
    return tz.localize(dt)

if __name__ == "__main__":
    main()