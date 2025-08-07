import discord
from discord_bot import DiscordBot
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = DiscordBot(intents=intents)
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    main()