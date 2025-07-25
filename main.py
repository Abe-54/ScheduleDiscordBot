import discord
from discord.ext import commands
from PIL import Image
import pytesseract
import requests
from io import BytesIO
import re
from collections import defaultdict
import cv2
import numpy as np

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('hello'):
            await message.channel.send(f'Hi there {message.author} ')

        if message.attachments.__len__() > 0:
            currentImageFound = message.attachments[0]

            print(f'Image found: {currentImageFound.url}')

            await message.channel.send(f'Attachment found: {message.attachments[0].url}')

            await message.channel.send(f'Extracting Data from {currentImageFound.url}')

            rawData = RawDataExtractor(currentImageFound)

            await message.channel.send(f'Processed Data: {ScheduleProcessor(rawData)}')


            # await message.channel.send(f'Extracted text: {ScheduleExtractor(currentImageFound)}')

        print(f'Message from {message.author}: {message.content}')

def RawDataExtractor(scheduleImg):
    response = requests.get(scheduleImg.url)

    if response.status_code == 200:
        print(f'Extracting text from {scheduleImg}')
        img = Image.open(BytesIO(response.content))

        # Convert PIL Image to OpenCV format (NumPy array)
        img_cv = np.array(img)
        # Convert RGB to BGR (OpenCV uses BGR by default)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)

        print('Extracting text from image')
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        # print(f'Left extracted: {data['left']}')
        # print(f'Top extracted: {data['top']}')
        print(f'Text extracted: {data['text']}')

        # ShowTextBounderies(data, img_cv)

        return data
    else:
        print(f'Error: {response.status_code}')
        return 'Failed to extract text'

def ScheduleProcessor(scheduleData):
    # Days of the week in order
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # Initialize an empty dictionary to store the parsed data
    employee_schedule = {}

    # for i, text in enumerate(scheduleData['text']):
      # For now, use hardcoded values
    leftThreshold = 220
    headerTop = 142
    employeeNames = []

    # TODO: Replace with runtime detection later
    # leftThreshold = detect_left_boundary(ocr_data)
    # headerTop = find_header_position(ocr_data)

    for i in range(0, len(scheduleData["text"])):

        if(scheduleData['left'][i] < leftThreshold and scheduleData['top'][i] > headerTop and "," in scheduleData['text'][i]):
            # nameIndicies.append(i)
            currIndex = i
            currentEmployeeParts = []
            while (currIndex < len(scheduleData["text"]) and scheduleData["text"][currIndex] != ''):
                currentEmployeeParts.append(scheduleData["text"][currIndex].strip())
                currIndex = currIndex + 1
            
            current_employee = " ".join(currentEmployeeParts).strip()
            
            if ", " in current_employee:
                parts = current_employee.split(", ", 1)
                if len(parts) == 2:
                    last_name, first_name = parts
        
                first_name = first_name.strip()
                last_name = last_name.strip()

            employeeNames.append(f"{first_name} {last_name}")

    print(employeeNames)

    # # Ensure the last employee is added to the schedule
    # if employee_name:
    #     employee_schedule[employee_name] = employee_shifts
    
    return employee_schedule

def ShowTextBounderies(data, img_cv):
    for i in range(0, len(data["text"])):
        x = data["left"][i]
        y = data["top"][i]

        w = data["width"][i]
        h = data["height"][i]

  
        text = data["text"][i]
        conf = int(data["conf"][i])

        if conf > 70:
            text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
            cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #cv2.putText(img_cv, text, (x, y - 10), 
            #cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2)
            cv2.putText(img_cv, f"{x},{y}", (x, y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2)

    cv2.imshow('Image', img_cv)  # Also need to provide window name
    cv2.waitKey(0)  # Wait for key press
    cv2.destroyAllWindows()  # Clean up 

intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run('MTMyODkxNTkwODI5MDE1MDQ0MQ.GyAJuP.9MdnTgGStW6hdFQfm9ocJaGj-yrCLpeWIBqVSY')