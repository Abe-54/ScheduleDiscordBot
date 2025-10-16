from discord import app_commands, Interaction
from utils.helpers import find_employee, format_employee_schedule

def setup_schedule_command(bot, guild_id):
    @bot.tree.command(name="schedule", description="Show schedule for an employee", guild=guild_id)
    @app_commands.describe(employee="The employee's name")
    async def schedule_command(interaction: Interaction, employee: str):
        if not bot.schedules:
            await interaction.response.send_message("❌ No schedule data loaded.")
            return
        
        employee_schedule = find_employee(bot, employee)
        if not employee_schedule:
            await interaction.response.send_message(f"❌ Employee '{employee}' not found.")
            return
        
        schedule_text = format_employee_schedule(bot, employee_schedule["name"], employee_schedule["schedule"])
        await interaction.response.send_message(schedule_text)