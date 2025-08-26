from google import genai
import requests
import os
from typing import List, Optional
from PIL import Image
import io
from pydantic import BaseModel, Field

class Week(BaseModel):
    from_date: str = Field(alias="from")
    to_date: str = Field(alias="to")

class Employee(BaseModel):
    name: str
    Monday: Optional[str] = None
    Tuesday: Optional[str] = None
    Wednesday: Optional[str] = None
    Thursday: Optional[str] = None
    Friday: Optional[str] = None
    Saturday: Optional[str] = None
    Sunday: Optional[str] = None

class Schedule(BaseModel):
    week: Week
    employees: List[Employee]  # Changed from Dict to List

class ScheduleDataProcessor:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
    async def extract_schedule_with_ai(self, image_url: str) -> Optional[dict]:
        """Extract schedule using Gemini Vision with structured output."""
        
        # Step 1: Download and convert image
        try:
            print(f"Downloading image from: {image_url}")
            response = requests.get(image_url)
            response.raise_for_status()
            pil_image = Image.open(io.BytesIO(response.content))
            print(f"Image ready: {pil_image.format}, Size: {pil_image.size}")
        except Exception as img_err:
            print(f"Error processing image: {img_err}")
            return None
        
        # Step 2: Call Gemini API with structured output
        try:
            prompt = """
            Extract the work schedule from this image.
            Include the week date range and each employee's daily work hours.
            Use null for days when employees are not working.
            Include any notes like PTO or sick days in the time slot.
            For each employee, include their name and their schedule for each day of the week.
            """
            
            print("Calling Gemini API...")
            gemini_response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, pil_image],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Schedule,
                }
            )
            
            # Use the parsed response directly
            schedule: Schedule = gemini_response.parsed
            employee_count = len(schedule.employees)
            print(f"Successfully extracted schedule with {employee_count} employees")
            
            # Convert to your original dict format for Discord bot compatibility
            return {
                "Week": {
                    "From": schedule.week.from_date,
                    "To": schedule.week.to_date
                },
                "Employees": {
                    emp.name: {
                        "Monday": emp.Monday,
                        "Tuesday": emp.Tuesday,
                        "Wednesday": emp.Wednesday,
                        "Thursday": emp.Thursday,
                        "Friday": emp.Friday,
                        "Saturday": emp.Saturday,
                        "Sunday": emp.Sunday,
                    }
                    for emp in schedule.employees
                }
            }
            
        except Exception as gemini_err:
            print(f"Error calling Gemini API: {gemini_err}")
            return None