import discord
from discord_bot import DiscordBot
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
            await interaction.response.send_message("❌ No schedule data loaded. Please upload a schedule image first!")
            return
        
        employee_schedule = _find_employee(bot, employee)
    
        if not employee_schedule:
            await interaction.response.send_message(f"❌ Employee '{employee}' not found.")
            return

        # Search for employee
        schedule_text = _format_employee_schedule(bot, employee_schedule['name'], employee_schedule['schedule'])
        await interaction.response.send_message(schedule_text)

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