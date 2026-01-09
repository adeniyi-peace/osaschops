from datetime import datetime
import pytz
from django.conf import settings

def is_store_currently_open(store):
    # 1. Check the Master Switch first
    if not store.is_store_open:
        return False, "The store is manually closed by the owner."

    # 2. Get current time in your timezone (e.g., Africa/Lagos)
    tz = pytz.timezone(settings.TIME_ZONE)
    now = datetime.now(tz)
    current_day_index = now.weekday()  # Monday is 0, Sunday is 6
    current_time = now.time()

    # 3. Look up today's schedule from the database
    try:
        today_schedule = store.hours.get(day=current_day_index)
    except store.hours.model.DoesNotExist:
        return False, "Schedule not set for today."

    # 4. Check if toggled open and if within time range
    if not today_schedule.is_open:
        return False, "We are closed today."

    if today_schedule.opening_time <= current_time <= today_schedule.closing_time:
        return True, "Open for frying!"
    
    return False, f"We open at {today_schedule.opening_time.strftime('%I:%M %p')} today."