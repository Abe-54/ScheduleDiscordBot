# Schedule Reader Discord Bot

A Discord bot that extracts work schedules from images using Google's Gemini AI.

## Features

*   **Image Processing**: Upload schedule images to automatically extract employee data.
*   **AI-Powered**: Uses Gemini 2.5 Flash for accurate text recognition.
*   **Slash Commands**: Modern Discord slash command support.
*   **Real-time Feedback**: Loading indicators and typing status while processing.

## Status

**Work in Progress (WIP)** - This project is under active development and may contain bugs. Please report any issues you encounter.

## Setup

1.  **Install Dependencies**

    ```bash
    pip install discord.py google-genai pillow pydantic python-dotenv requests
    ```

2.  **Environment Variables**

    Create a `.env` file with the following:

    ```
    DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    GUILD_ID=YOUR_DISCORD_SERVER_ID
    ```

3.  **Run the Bot**

    ```bash
    python main.py
    ```

## Usage

1.  Upload a schedule image to any channel.
2.  The bot automatically processes and extracts employee schedules.
3.  Use `/help` to see available commands.

## Tech Stack

*   **Discord.py**: Discord API wrapper.
*   **Google Gemini AI**: Image-to-text processing.
*   **Pydantic**: Data validation.
*   **PIL (Pillow)**: Image processing.

## Credits

*   Abraham Rubio (Game Programmer, Game Designer & Artist)

## What I Learned

This project provided valuable experience in several areas:

*   **API Integration**: Successfully integrated with the Google Gemini AI and Discord APIs.
*   **Image Processing**: Learned to download, open, and prepare images for AI analysis.
*   **Asynchronous Programming**: Deepened my understanding of `async` and `await` for efficient bot operations.
*   **Discord Bot Development**: Gained experience building a functional and interactive Discord bot with slash commands.
*   **Error Handling**: Implemented robust error handling to gracefully manage potential issues during image processing and API calls.

## License

MIT License

Copyright (c) 2025 [Abraham Rubio]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
