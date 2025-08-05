import discord
from discord_bot import DiscordBot

def main():
    intents = discord.Intents.default()
    intents.message_content = True
    
    TOKEN = 'MTMyODkxNTkwODI5MDE1MDQ0MQ.GyAJuP.9MdnTgGStW6hdFQfm9ocJaGj-yrCLpeWIBqVSY'
    
    bot = DiscordBot(intents=intents)
    bot.run(TOKEN)

if __name__ == "__main__":
    main()