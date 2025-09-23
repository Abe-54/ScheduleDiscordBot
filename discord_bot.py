import discord
from discord.ext import commands
from data_processor import ScheduleDataProcessor
import asyncio

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
        
        # # Process image attachments
        # if message.attachments:
        #     await self._process_image_attachment(message)
    
    async def _process_image_attachment(self, scheduleImage: discord.Attachment, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Create a task to keep typing indicator alive
        typing_task = asyncio.create_task(self._keep_typing(interaction.channel))
        
        try:
            # Extract and process schedule data
            data = await self.processor.extract_schedule_with_ai(scheduleImage.url)
            print(f"Extracted Data: {data}")
            
            # Stop the typing indicator
            typing_task.cancel()
            
            if not data:
                await interaction.followup.send('❌ Failed to extract data from image.')
                return

            self.current_week = data["Week"]
            self.schedules = data["Employees"]
            
            # Send success message
            week_info = data["Week"]
            from_date = week_info.get("From", "Unknown")
            to_date = week_info.get("To", "Unknown")
            employee_count = len(data["Employees"])
            
            await interaction.followup.send(
                f'✅ Loaded schedules for {employee_count} employees from {from_date} to {to_date}\n'
                f'Use `/help` to see available commands!'
            )
            
        except Exception as e:
            typing_task.cancel()
            print(f'Error processing image: {e}')
            await interaction.followup.send('❌ An error occurred while processing the image.')

    async def _keep_typing(self, channel):
        """Keep the typing indicator active."""
        try:
            while True:
                async with channel.typing():
                    await asyncio.sleep(8)  # Refresh every 8 seconds
        except asyncio.CancelledError:
            pass  # Task was cancelled, stop typing