from typing import Optional
import discord
from discord_bot import DiscordBot
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = DiscordBot(command_prefix="!", intents=intents)

    GUILD_ID = discord.Object(int(os.getenv('DEV_GUILD_ID')))

    #Commands
    @bot.tree.command(name="help", description="show all available commands", guild=GUILD_ID)
    async def helpCommand(interaction: discord.Interaction):
        await interaction.response.send_message("All Available Commands:") 
    

    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    main()