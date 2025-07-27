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
        # print(f'Top extracted: {data['top']}')s
        # print(f'Text extracted: {data['text']}')

        # ShowTextBounderies(data, img_cv)

        return data
    else:
        print(f'Error: {response.status_code}')
        return 'Failed to extract text'

def ScheduleProcessor(scheduleData):
    
    # Initialize an empty dictionary to store the parsed data
    employeeSchedule = {}

    # for i, text in enumerate(scheduleData['text']):
      # For now, use hardcoded values
    leftNameThreshold = 220
    headerTopThreshold = 142
    Employees = {}
    # Days of the week in order
    daysOfTheWeek = {"Mon": (0,0), "Tue": (0,0), "Wed": (0,0), "Thu": (0,0), "Fri": (0,0), "Sat": (0,0), "Sun": (0,0)}


    # TODO: Replace with runtime detection later
    # leftThreshold = detect_left_boundary(ocr_data)
    # headerTop = find_header_position(ocr_data)

    # Grab All Employee Names & Coordinates AND Day of the Week Coordinates
    for i in range(0, len(scheduleData["text"])):
        #Names
        if(scheduleData['left'][i] < leftNameThreshold and scheduleData['top'][i] > headerTopThreshold and "," in scheduleData['text'][i]):
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

            Employees[f"{first_name} {last_name}"] = {"coordinates": (scheduleData['left'][i], scheduleData['top'][i]), "TimeSlots": {}}

        #Day Coordinates
        if scheduleData["text"][i] in daysOfTheWeek:
            daysOfTheWeek[scheduleData["text"][i]] ={"coordinates": (scheduleData['left'][i], scheduleData['top'][i])}
            
    tolerance = 20

    # print(Employees)
    # print(daysOfTheWeek)

    #Grab The Time-Slots
    for employee, employeeData in Employees.items():
        # print(f"Employee: {employee}, Data: {employeeData}")

        employeeTop = employeeData["coordinates"][1]
        # print(f"Employee Top: { employee[1][1]}")
        for day, dateData in daysOfTheWeek.items():
            dayLeft = dateData["coordinates"][0]
            # print(f"Day Left: { day[1][0]}")
            for i in range(len(scheduleData["text"])):
                timeslotTop = scheduleData["top"][i]
                timeslotLeft = scheduleData["left"][i]

                if (abs(timeslotTop - employeeTop) <= tolerance and 
                    abs(timeslotLeft - dayLeft) <= tolerance):

                    # print(f"{scheduleData["text"][i]}")

                    if scheduleData["text"][i].strip():  # Not empty
                        #[day[0]] = (scheduleData["text"][i])
                        employeeData["TimeSlots"][day] = scheduleData["text"][i]
                        # print(f"{scheduleData["text"][i]}")
                        # print(f"TimeSlots: {employeeData["TimeSlots"]}")
            
            
            # if timeslots:
            #     print(f"{employee[0]} on {day[0]}: {timeslots}")
            # else:
            #     print(f"{employee[0]} on {day[0]}: No shift")
        print(f"Employee: {employee}, Data: {employeeData}")

   

    # # Ensure the last employee is added to the schedule
    # if employee_name:
    #     employee_schedule[employee_name] = employee_shifts
    
    return employeeSchedule

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