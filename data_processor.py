import requests
import pytesseract
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from typing import Dict, Any, Optional


class ScheduleDataProcessor:
    """Handles OCR extraction and schedule data processing."""
    
    def __init__(self):
        self.left_name_threshold = 220
        self.header_top_threshold = 142
        self.tolerance = 20
        self.days_of_week = [
            "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
        ]
    
    def extract_raw_data(self, image_url: str) -> Optional[Dict[str, Any]]:
        """Extract raw OCR data from image URL."""
        try:
            response = requests.get(image_url)
            if response.status_code != 200:
                print(f'Error downloading image: {response.status_code}')
                return None
            
            print(f'Extracting text from {image_url}')
            img = Image.open(BytesIO(response.content))
            
            # Convert PIL Image to OpenCV format
            img_cv = np.array(img)
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
            
            print('Running OCR on image')
            data = pytesseract.image_to_data(
                img, output_type=pytesseract.Output.DICT
            )
            
            # Optionally show text boundaries for debugging
            # self._show_text_boundaries(data, img_cv)
            
            return data
            
        except Exception as e:
            print(f'Error extracting data: {e}')
            return None
    
    def process_schedule(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw OCR data into structured schedule format."""
        if not raw_data:
            return {}
        
        schedule = {"Week": {}, "Employees":{}}
        employees = {}
        day_coordinates = {}
        
        # Extract week dates, employee names, and day coordinates
        self._extract_week_info(raw_data, schedule)
        self._extract_employees(raw_data, employees)
        self._extract_day_coordinates(raw_data, day_coordinates)
        
        # Extract time slots for each employee
        self._extract_time_slots(raw_data, employees, day_coordinates)
        
        # Format final schedule
        for employee, data in employees.items():
            schedule["Employees"][employee] = {"Schedule": data["TimeSlots"]}
        
        print(f"Processed schedule data: {schedule}")
        return schedule
    
    def _extract_week_info(self, data: Dict[str, Any], schedule: Dict[str, Any]):
        """Extract week date range from OCR data."""
        for i, text in enumerate(data["text"]):
            if text == "Schedules" and i + 4 < len(data["text"]):
                from_date = data["text"][i + 2]
                to_date = data["text"][i + 4]
                schedule["Week"] = {"From": from_date, "To": to_date}
                break
    
    def _extract_employees(self, data: Dict[str, Any], employees: Dict[str, Any]):
        """Extract employee names and their coordinates."""
        for i, text in enumerate(data["text"]):
            if (data['left'][i] < self.left_name_threshold and 
                data['top'][i] > self.header_top_threshold and 
                "," in text):
                
                # Collect full employee name
                curr_index = i
                name_parts = []
                while (curr_index < len(data["text"]) and 
                       data["text"][curr_index] != ''):
                    name_parts.append(data["text"][curr_index].strip())
                    curr_index += 1
                
                full_name = " ".join(name_parts).strip()
                
                if ", " in full_name:
                    parts = full_name.split(", ", 1)
                    if len(parts) == 2:
                        last_name, first_name = parts
                        formatted_name = f"{first_name.strip()} {last_name.strip()}"
                        
                        employees[formatted_name] = {
                            "coordinates": (data['left'][i], data['top'][i]),
                            "TimeSlots": {}
                        }
    
    def _extract_day_coordinates(self, data: Dict[str, Any], day_coordinates: Dict[str, Any]):
        """Extract day of week coordinates."""
        for i, text in enumerate(data["text"]):
            if text in self.days_of_week:
                day_coordinates[text] = {
                    "coordinates": (data['left'][i], data['top'][i]),
                    "index": i
                }
    
    def _extract_time_slots(self, data: Dict[str, Any], employees: Dict[str, Any], 
                           day_coordinates: Dict[str, Any]):
        """Extract time slots for each employee and day."""
        for employee, employee_data in employees.items():
            employee_top = employee_data["coordinates"][1]
            
            for day, day_data in day_coordinates.items():
                day_left = day_data["coordinates"][0]
                
                for i in range(len(data["text"])):
                    slot_top = data["top"][i]
                    slot_left = data["left"][i]
                    
                    if (abs(slot_top - employee_top) <= self.tolerance and 
                        abs(slot_left - day_left) <= self.tolerance):
                        
                        if data["text"][i].strip():
                            time_slot = self._collect_time_elements(data, i)
                            date_info = data['text'][day_data['index'] + 1] if day_data['index'] + 1 < len(data['text']) else ""
                            employee_data["TimeSlots"][f"{day} {date_info}"] = time_slot
    
    def _collect_time_elements(self, data: Dict[str, Any], center_index: int) -> str:
        """Collect time elements around a center index."""
        start_idx = max(0, center_index - 4)
        end_idx = min(len(data["text"]), center_index + 4)
        
        time_elements = []
        for i in range(start_idx, end_idx):
            text = data["text"][i].strip()
            if text:
                time_elements.append(text)
        
        return " ".join(time_elements)
    
    def _show_text_boundaries(self, data: Dict[str, Any], img_cv: np.ndarray):
        """Display text boundaries for debugging (optional)."""
        for i in range(len(data["text"])):
            x, y = data["left"][i], data["top"][i]
            w, h = data["width"][i], data["height"][i]
            conf = int(data["conf"][i])
            
            if conf > 70:
                cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img_cv, f"{x},{y}", (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2)
        
        cv2.imshow('Image', img_cv)
        cv2.waitKey(0)
        cv2.destroyAllWindows()