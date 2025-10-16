import discord
from dotenv import load_dotenv

import os
from commands.connect_google_command import setup_connect_google_command
from commands.help_command import setup_help_command
from commands.new_schedule_command import setup_new_schedule_command
from commands.schedule_command import setup_schedule_command
from commands.sync_calendar_command import setup_sync_calendar_command
from discord_bot import DiscordBot

load_dotenv()

def main():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = DiscordBot(command_prefix="!", intents=intents)

    GUILD_ID = discord.Object(int(os.getenv('DEV_GUILD_ID')))

    # Register commands
    setup_help_command(bot, GUILD_ID)
    setup_schedule_command(bot, GUILD_ID)
    setup_new_schedule_command(bot, GUILD_ID)
    setup_connect_google_command(bot, GUILD_ID)
    setup_sync_calendar_command(bot, GUILD_ID)
    
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    main()