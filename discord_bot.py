import discord
from discord.ext import commands
from discord import app_commands
from data_processor import ScheduleDataProcessor
from typing import Optional


class DiscordBot(commands.Bot):
    """Discord bot for processing schedule images."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processor = ScheduleDataProcessor()
        self.schedules = {}  # Store extracted schedules
        self.current_week = None  # Store current week info
    
    async def on_ready(self):
        """Called when the bot is ready."""
        print(f'Logged on as {self.user}!')

        try:
            guild = discord.Object(id=1328907522299658260)
            synced= await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to guild {guild.id}")

        except Exception as e:
            print(f'Error syncing commands: {e}')
    
    async def on_message(self, message: discord.Message):
        """Handle incoming messages."""
        # Ignore messages from the bot itself
        if message.author == self.user:
            return
        
        # Process image attachments
        if message.attachments:
            await self._process_image_attachment(message)
    
    async def _process_image_attachment(self, message: discord.Message):
        """Process the first image attachment in a message."""
        attachment = message.attachments[0]
        print(f'Image found: {attachment.url}')
        
        # Send loading message with single emoji
        loading_msg = await message.channel.send('🔄 Extracting data from image...')
        
        # Start typing indicator
        async with message.channel.typing():
            try:
                # Extract and process schedule data
                data = await self.processor.extract_schedule_with_ai(attachment.url)
                print(f"Extracted Data: {data}")
                
                if not data:
                    await loading_msg.edit(content='❌ Failed to extract data from image.')
                    return

                self.current_week = data["Week"]
                self.schedules = data["Employees"]
                
                # Edit message with success
                week_info = data["Week"]
                from_date = week_info.get("From", "Unknown")
                to_date = week_info.get("To", "Unknown")
                employee_count = len(data["Employees"])
                
                await loading_msg.edit(content=
                    f'✅ Loaded schedules for {employee_count} employees from {from_date} to {to_date}\n'
                    f'Use `/help` to see available commands!'
                )
                
            except Exception as e:
                print(f'Error processing image: {e}')
                await loading_msg.edit(content='❌ An error occurred while processing the image.')