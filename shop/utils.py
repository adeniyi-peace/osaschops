from datetime import datetime
import pytz
from django.conf import settings

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
    # 1. Check the Master Switch first
    if not model.is_open:
        return False, "The model is manually closed by the owner."

    current_day_index, current_time = get_current_day_and_time()

    # 3. Look up today's schedule from the database
    try:
        today_schedule = model.hours.get(day=current_day_index)
    except model.hours.model.DoesNotExist:
        return False, "Schedule not set for today."

    # 4. Check if toggled open and if within time range
    if not today_schedule.is_open:
        return False, "We are closed today."

    if today_schedule.opening_time <= current_time <= today_schedule.closing_time:
        return True, "Open for frying!"
    
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
            if i == 0 and current_time < hours.open_time:
                return False, f"We open at {hours.open_time.strftime('%I:%M %p')} today."
            
            elif i == 1:
                return False, f"We open tommorow at {hours.open_time.strftime('%I:%M %p')}."
            
            elif i > 1:
                return False, f"We open {hours.get_day_display} at {hours.open_time.strftime('%I:%M %p')}."


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