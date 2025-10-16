from datetime import datetime, timedelta
import json
from discord import app_commands, Interaction
import discord
import pytz

from calendar_api import add_event_to_new_calendar, create_new_calendar, get_events_between, get_primary_calendar, test_calendar_connection
from discord_view import ConfirmView
from utils.helpers import combine_day_and_time, find_employee, find_existing_work_calendar, verify_sync_prerequisites

def setup_sync_calendar_command(bot, guild_id):
    @bot.tree.command(name="sync_calendar", description="Sync an employee's schedule to your calendar", guild=guild_id)
    @app_commands.describe(employee_name="The employee whose schedule you want to sync")
    async def syncWorkCalendarCommand(interaction: discord.Interaction, employee_name: str):
        """Sync selected employee schedule to user's Google Calendar"""
        user_id = interaction.user.id

        # Run prerequisite checks
        employee_schedule = await verify_sync_prerequisites(
            bot, interaction, employee_name, test_calendar_connection, find_employee
        )
        if not employee_schedule:
            return  # early exit if checks failed

        # Loop over days, add events
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
        calendar_name = None

        # ✅ Calendar selection logic (streamlined)
        if use_primary:
            calendar_id = "primary"
            calendar_name = get_primary_calendar().get("summary")
        else:
            # Check for existing "Work Schedule" calendar
            existing_calendar = find_existing_work_calendar()

            if existing_calendar:
                calendar_id = existing_calendar["id"]
                calendar_name = existing_calendar["summary"]
            else:
                # Create if none exists
                new_calendar = create_new_calendar()
                calendar_id = new_calendar["id"]
                calendar_name = new_calendar["summary"]

        await interaction.followup.send(f"⏳ Syncing events using {calendar_name} ...", ephemeral=True)

        results = []
        for day, times in employee_schedule["schedule"].items():
            if not times: 
                continue
            
            # Example: "09:00 AM - 05:00 PM"
            try:
                parts = times.split("-")
                start_str, end_str = parts[0].strip(), parts[1].strip()
                start_time = combine_day_and_time(week_start, day, start_str)
                end_time   = combine_day_and_time(week_start, day, end_str)

                utc = pytz.UTC
                start_utc = start_time.astimezone(utc)
                end_utc = end_time.astimezone(utc)

                events = get_events_between(
                        calendar_id,
                        start_utc - timedelta(minutes=10),
                        end_utc + timedelta(minutes=10),
                        tz_name="UTC",
                    )

                shift_desc = f"{employee_name} shift".casefold()
                already_exists = False

                for ev in events:
                    ev_desc = ev.get("description", "").strip().casefold()
                    ev_start_str = ev.get("start", {}).get("dateTime")
                    ev_end_str = ev.get("end", {}).get("dateTime")

                    if not ev_start_str or not ev_end_str:
                        continue

                    # Convert event times from string to UTC datetime
                    ev_start = datetime.fromisoformat(ev_start_str.replace("Z", "+00:00"))
                    ev_end = datetime.fromisoformat(ev_end_str.replace("Z", "+00:00"))

                    # Compare name & time match
                    if (
                        ev_desc == shift_desc
                        and abs((ev_start - start_utc).total_seconds()) < 60
                        and abs((ev_end - end_utc).total_seconds()) < 60
                    ):
                        already_exists = True
                        break

                if already_exists:
                    results.append(f"⏩ {day}: skipped — already created")
                    continue

                event = add_event_to_new_calendar(
                    user_id, f"{employee_name} shift", start_time, end_time, calendar_id
                )
                link = event.get("htmlLink", "(no link)")
                results.append(f"✅ {day}: synced → {link}")

            except:
                results.append(f"⚠️ Could not sync {day}: {times}")

        await interaction.followup.send("\n".join(results))
