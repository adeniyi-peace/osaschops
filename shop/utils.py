from datetime import datetime
import pytz
from django.conf import settings
from django.core.files.base import ContentFile

from PIL import Image
from io import BytesIO

from vendor.models import BusinessDay

def get_current_day_and_time(timezone_name=settings.TIME_ZONE):
    """
    Returns the current day of the week
    """
    tz = pytz.timezone(timezone_name)
    now = datetime.now(tz)

    current_day = now.weekday()
    current_time = now.time()

    return current_day, current_time

def is_store_currently_open(model):

    current_day_index, current_time = get_current_day_and_time()

    # 3. Look up today's schedule from the database
    try:
        today_schedule = model.get(day=current_day_index)
    except BusinessDay.DoesNotExist:
        return False, "Schedule not set for today."

    # 4. Check if toggled open and if within time range
    if not today_schedule.is_open or today_schedule.opening_time > current_time or current_time > today_schedule.closing_time:
        for i in range(7):
            """
            Get the next open day
            if i == 0, next open day is today
            if i == 1, next day is tommorow
            """
            day = get_next_day(number=i)

            # Filters through the related business hour linked to Vendor 
            # checking the day and if it is opened for that day
            hours = model.filter(day=day, is_open=True).first()

            if hours:
                if i == 0 and current_time < hours.opening_time:
                    return False, f"We open at {hours.opening_time.strftime('%I:%M %p')} today."
                
                elif i == 1:
                    return False, f"We open tommorow at {hours.opening_time.strftime('%I:%M %p')}."
                
                elif i > 1:
                    return False, f"We open {hours.get_day_display} at {hours.opening_time.strftime('%I:%M %p')}."
                
        return False, "We are closed today."

    if today_schedule.opening_time <= current_time <= today_schedule.closing_time:
        return True, "Open for frying!"
    
    


def get_next_day(number, timezone_name="Africa/lagos"):
    """
    Returns the next day of the week
    """
    tz = pytz.timezone(timezone_name)
    now =datetime.now(tz)

    # Modulo 7 ensures that day is not greater than 6
    # I.e if  (now.weekday() + number)==7, day will be 0
    # And if (now.weekday() + number) == 9, day will be 2
    day = (now.weekday() + number) % 7

    next_day = day

    return next_day


def compress_image(image, new_width):
    try:
        img = Image.open(image)
        img.verify()

        img = Image.open(image)

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        
        width, height = img.size
        
        if width > new_width:
            new_height = int((new_width / width) * height)
            img = img.resize((new_width, new_height), Image.LANCZOS)

        temp_img = BytesIO()
        
        img.save(temp_img, format="WEBP", quality=70, optimize=True)
        temp_img.seek(0)

        name, _ = image.name.lower().split(".")

        img = f"{name}.webp"

        image.save(img, ContentFile(temp_img.read()), save=False)

    except (IOError, SyntaxError) as e:
        raise ValueError(f"The uploaded file is not a valid image. -- {e}")
