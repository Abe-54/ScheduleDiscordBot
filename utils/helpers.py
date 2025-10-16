from typing import Optional
import pytz
from datetime import datetime, timedelta

from calendar_api import get_calendar_list

def find_employee(bot, search_name: str) -> dict:
    """Find employee by name (case-insensitive, partial match)."""
    search_name = search_name.lower()
    
    for emp_name, schedule in bot.schedules.items():
        if search_name in emp_name.lower():
            return {"name": emp_name, "schedule": schedule}
    
    return None

def format_employee_schedule(self, name: str, schedule: dict) -> str:
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

def combine_day_and_time(week_start, day_name, time_str):
    # Map weekday strings to offsets
    day_index = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].index(day_name)
    tz = pytz.timezone("America/New_York")

    # Trim things like "09:00 AM"
    t = datetime.strptime(time_str.strip(), "%I:%M %p").time()
    dt = datetime.combine(week_start + timedelta(days=day_index), t)
    return tz.localize(dt)

def find_existing_work_calendar(target_name: Optional[str] ="Work Schedule"):
    calendars = get_calendar_list()
    for calendar in calendars:
        if calendar.get("summary", "").lower() == target_name.lower():
            return calendar
    return None

async def verify_sync_prerequisites(bot, interaction, employee_name, test_calendar_connection_func, find_employee_func):
    """Verify all prerequisites before syncing calendar."""
    # 1. Check if schedules exist
    if not hasattr(bot, "schedules") or not bot.schedules:
        await interaction.response.send_message(
            "❌ No schedule data loaded. Upload a schedule first!",
            ephemeral=True,
        )
        return None

    # 2. Check if employee exists
    employee_schedule = find_employee_func(bot, employee_name)
    if not employee_schedule:
        await interaction.response.send_message(
            f"❌ Employee '{employee_name}' not found!",
            ephemeral=True,
        )
        return None

    # 3. Check Google Calendar connection
    is_connected = test_calendar_connection_func()
    if not is_connected:
        await interaction.response.send_message(
            "❌ Failed to connect to Google Calendar.",
            ephemeral=True,
        )
        return None

    # 4. If all good, return the employee data
    return employee_schedule