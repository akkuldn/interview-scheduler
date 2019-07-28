"""
This module contains business logic that wraps around the Google calendar module
We use this extensively in the routes.py of the qxf2_scheduler application
"""

import base_gcal as gcal
import datetime
from datetime import timedelta
import pytz

TIMEZONE_STRING = '+05:30'
DAY_START_HOUR = 9
DAY_END_HOUR = 17

def get_free_slots(busy_slots, day_start, day_end):
    "Return the free slots"
    """
    Logic:
    There are 6 types of use cases for us:
    a) A busy slot that ends before day start
        - we ignore
    b) A busy slot that starts after the day end
        - we ignore
    c) A busy slot that starts before the day start and ends after day end
        - we say there are no free slots in that day
    d) A busy slot that starts before day start but ends before day end
        - we set the start of the first free slot to the end of this busy slot 
    e) A busy slot that starts (after day start, before day end) but ends after day end
        - we set the end of the last free slot to be the start of this busy slot
    f) A busy slot that starts after day start and ends before day end
        - we accept both ends points of this slot
    """
    free_slots = []
    for busy_slot in busy_slots:
        if busy_slot['end'] < day_start:
            continue 
        elif busy_slot['start'] > day_end:
            continue 
        elif busy_slot['start'] < day_start and busy_slot['end'] > day_end:
            break 
        elif busy_slot['start'] < day_start and busy_slot['end'] < day_end:
            free_slots.append(busy_slot['end'])
        elif busy_slot['start'] > day_start and busy_slot['end'] > day_end:
            free_slots.append(busy_slot['start'])
        else:
            #If we make it this far and free_slots is still empty
            #It means the start of the free slot is the start of the day
            if len(free_slots) == 0:
                free_slots.append(day_start)
            free_slots.append(busy_slot['start'])
            free_slots.append(busy_slot['end'])
    #If we have an odd number of values in free_slots
    #It means that we need to close one interval with end of day
    if len(free_slots)%2 == 1:
        if free_slots[-1]==day_end:
            free_slots = free_slots[:-1]
        else:
            free_slots.append(day_end)
    
    return free_slots

def get_busy_slots_for_date(email_id,fetch_date,debug=False):
    "Get the free events for a given date"
    service = gcal.base_gcal()
    busy_slots = gcal.get_busy_slots_for_date(service,email_id,fetch_date,timeZone=gcal.TIMEZONE,debug=debug)

    return busy_slots


def get_events_for_date(email_id, fetch_date, maxResults=240,debug=False):
    "Get all the events for a fetched date"
    service = gcal.base_gcal()
    events = gcal.get_events_for_date(service,email_id,fetch_date,debug=debug)

    return events

def process_time_to_gcal(given_date,hour_offset=None):
    "Process a given string to a gcal like datetime format"
    processed_date = gcal.process_date_string(given_date)
    if hour_offset is not None:
        processed_date = processed_date.replace(hour=hour_offset)
    processed_date = gcal.process_date_isoformat(processed_date)
    processed_date = str(processed_date).replace('Z',TIMEZONE_STRING)

    return processed_date


#----START OF SCRIPT
if __name__ == '__main__':
    email = 'mak@qxf2.com'
    date = '2019-07-29'
    print("\n=====HOW TO GET ALL EVENTS ON A DAY=====")
    get_events_for_date(email, date, debug=True)
    print("\n=====HOW TO GET BUSY SLOTS=====")
    busy_slots = get_busy_slots_for_date(email,date,debug=True)
    print("\n=====HOW TO GET FREE SLOTS=====")
    day_start = process_time_to_gcal(date,DAY_START_HOUR)
    day_end = process_time_to_gcal(date,DAY_END_HOUR)
    free_slots = get_free_slots(busy_slots,day_start,day_end)
    print("Free slots for {email} on {date} are:".format(email=email, date=date))
    for i in range(0,len(free_slots),2):
        print(free_slots[i],'-',free_slots[i+1])