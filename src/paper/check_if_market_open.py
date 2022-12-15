# import dependencies
import pandas_market_calendars as mcal
from datetime import datetime, timedelta

# Get if market day
def get_if_market_day():
    today = datetime.now()
    yesterday = today - timedelta(1)
    nyse = mcal.get_calendar('NYSE')
    days = nyse.valid_days(start_date=yesterday, end_date=today)
    for day in days:
        if day.date() == today.date():
            return True
    return False