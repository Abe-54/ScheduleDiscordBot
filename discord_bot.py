import discord
from data_processor import ScheduleDataProcessor
from typing import Optional


class DiscordBot(discord.Client):
    """Discord bot for processing schedule images."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processor = ScheduleDataProcessor()
    
    async def on_ready(self):
        """Called when the bot is ready."""
        print(f'Logged on as {self.user}!')
    
    async def on_message(self, message: discord.Message):
        """Handle incoming messages."""
        # Ignore messages from the bot itself
        if message.author == self.user:
            return
        
        # print(f'Message from {message.author}: {message.content}')
        
        # Process image attachments
        if message.attachments:
            await self._process_image_attachment(message)
    
    async def _process_image_attachment(self, message: discord.Message):
        """Process the first image attachment in a message."""
        attachment = message.attachments[0]
        print(f'Image found: {attachment.url}')
        
        await message.channel.send(f'Extracting data from {attachment.url}')
        
        try:
            # Extract and process schedule data
            raw_data = self.processor.extract_raw_data(attachment.url)
            if not raw_data:
                await message.channel.send('Failed to extract data from image.')
                return
            
            processed_data = self.processor.process_schedule(raw_data)
            if not processed_data or "Week" not in processed_data:
                await message.channel.send('Failed to process schedule data.')
                return
            
            # Send confirmation message
            week_info = processed_data["Week"]
            from_date = week_info.get("From", "Unknown")
            to_date = week_info.get("To", "Unknown")

            employee_info = processed_data["Employees"]
            
            await message.channel.send(
                f'Received schedules for {len(employee_info)} employees from {from_date} to {to_date}'
            )
            
            # TODO: Add more functionality here (save to database, format output, etc.)
            
        except Exception as e:
            print(f'Error processing image: {e}')
            await message.channel.send('An error occurred while processing the image.')
    
    # Future command methods can be added here
    async def setup_commands(self):
        """Setup slash commands (for future implementation)."""
        pass
    
    async def handle_schedule_query(self, employee_name: str) -> Optional[str]:
        """Handle schedule queries for specific employees (future feature)."""
        # TODO: Implement database lookup for employee schedules
        pass
    
    async def handle_schedule_export(self, format_type: str = "json") -> Optional[str]:
        """Export schedule data in various formats (future feature)."""
        # TODO: Implement schedule export functionality
        pass