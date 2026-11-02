'''
utility.py
utility functions for workouts project
'''

from time import perf_counter
import datetime
from datetime import timedelta

import math
import pandas as pd

from loguru import logger

def get_num_workout_days(entity):
    '''
    take a datetime "now" object and return the number of workout days for this month/year
    loop through the days of the month up to now
    if it's a su mo we fri sat, add 1
    retval is a list
    1st element- number of workout days 
    2nd element- number of weight days
    '''
    retval = [0,0]
    delta_1 = timedelta(days=1)
    x_now = datetime.datetime.now()
    x_1st = None

    # 1st day of this month/year, depending upon entity
    if entity == 'month':
        x_1st = datetime.datetime(x_now.year, x_now.month, 1)
    if entity == 'year':
        x_1st = datetime.datetime(x_now.year, 1, 1)

    x_start = x_1st

    while x_start <= x_now:
        # get day of the week of x_start
        dow = x_start.weekday()
        # Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
        #print (f"{dow}")

        # workout days
        # mon, wed, fri, sat, sun by definition
        if dow in [0,2,4,5,6]:
            retval[0] += 1

        # gym days
        # sun, thu by definition
        if dow in [3,6]:
            retval[1] += 1

        # increment
        x_start += delta_1

    return retval

def unixday_now():
    '''
    return now unixday
    '''
    day_of_now = datetime.datetime.now()
    unix_days_now = convert_date_to_unixdays(day_of_now)
    return unix_days_now

def convert_to_mins(hhmmss):
    '''
    hhmmss is actually hh:mm:ss
    convert to float minutes
    '''
    retval = 0.0
    if isinstance(hhmmss, float):
        return retval

    parsed_hhmmss = hhmmss.split(":")
    hrs = int(parsed_hhmmss[0])
    mins = int(parsed_hhmmss[1])
    secs = int(parsed_hhmmss[2])

    retval = (float) (60 * hrs)
    retval += (float) (mins)
    retval += (float) (secs)/ (float) (60)

    return round(retval,2)

def convert_date_to_unixdays(this_date):
    '''
    converts a datetime date to number of unixdays (since 1/1/70)
    '''
    # unix time unixtime
    base_1970 = datetime.datetime(1970, 1, 1)
    unixdays = (this_date - base_1970).days
    #         stamp = (dt - datetime(1970, 1, 1, tzinfo=self)) // SECOND

    return int(unixdays)

def convert_date_to_week(this_date):
    '''
    converts a datetime date to ww
    ww is 00 for days before the 1st monday of the year
    ww is 01 for the first monday of the year
    '''
    week = this_date.strftime("%W")

    #if this_date.strftime("%Y") == "2024":
    #    print(f"date- week {this_date} {week}")

    return int(week)


def convert_date(date_str):
    '''
    convert string to date
    # date- convert from str to python datetime
    # Wed 10/11/23
    '''
    # probably turn into a func
    date_pieces = date_str
    mdy = date_pieces[1].split("/")

    # tweak the century
    century = None
    if int(mdy[2]) > 90:
        century = 1900
    else:
        century = 2000

    yr = int(mdy[2]) + century
    month = int(mdy[0])
    dom = int(mdy[1])

    # unix time unixtime
    python_time = datetime.datetime(yr, month, dom)
    unixdays = convert_date_to_unixdays(python_time)

    # int values
    #retval = {
    #        "date": python_time,
    #        "year": int(yr),
    #        "month": int(month),
    #        "dom": int(dom),
    #        "unixdays": int(unixdays)
    #    }

    # str values
    retval = {
            "date": datetime.date(yr, month, dom), 
            "year": str(int(yr)),
            "month": str(int(month)),
            "dom": str(int(dom)),
            "doy": str(datetime.date(yr, month, dom).timetuple()[7]),
            "unixdays": str(unixdays)
        }

    return retval

def get_event(in_miles, in_descr):
    '''
    determine event
    # decide what kind of event this was
    # run/walk
    # bike
    # gym- 0 miles (actually, nan)
    # but stationary bike will also have 0 miles, so descr will contain "bike"
    '''
    retval = ''

    # if it's a string and contains bike, assign accordingly
    if isinstance(in_descr, str):
        if 'bike' in in_descr:
            retval = "bike"

        if 'sbike' in in_descr:
            retval = "sbike"

    if retval == '':
        if math.isnan(in_miles):
            retval = "gym"
        elif float(in_miles) > 5.0:
            retval = "bike"
        else:
            retval = "walk"

    return retval

def get_track_info(descr, minutes, laps):
    '''
    gets sec per lap and miles given the track desc and number of laps
    '''
    # lap values
    laps_per_miles = {
        "er": 12.8571,
        "wr": 10.4795,
        "sr": 9.3293,
        "nr": 18.0000,
        "trail winds": 9.5031,
        }

    # default values
    sec_per_lap = 0
    track_miles = 0

    # see if the track is in the dict
    if descr in laps_per_miles:
        # sec per lap
        sec_per_lap = 60 * minutes / laps
        sec_per_lap = round(sec_per_lap,2)

        # miles
        track_miles = float(laps / laps_per_miles[descr])
        track_miles = round(track_miles, 2)

    track_info = {
        'sec_per_lap': sec_per_lap,
        'track_miles': track_miles
    }
    return track_info


def counter_init(members):
    '''
    return counter initialized from list of members
    '''
    retval = {}
    for _m in members:
        retval[_m] = 0
    return retval

def counter_report(counter, counter_title, units="", show_total=True, skip_zero_values=False):
    '''
    takes counter dict and reports items and total. specify units if desired
    skip_zero_values default to False, set to True to skip 0 values
    '''
    # match count
    logger.info(counter_title)
    tot = 0
    for _name, _cnt in counter.items():
        # skip zero value?
        if skip_zero_values and _cnt == 0:
            continue

        # format for float if cnt is float
        if isinstance(_cnt, float):
            logger.info(f"  {_name} {_cnt:0.2f} {units}")
        else:
            logger.info(f"  {_name} {_cnt} {units}")
        tot += _cnt

    if show_total:
        if isinstance(tot, float):
            logger.info(f"  Total: {tot:0.2f} {units}")
        else:
            logger.info(f"  Total: {tot} {units}")

# initialize timer_counter
timer_counter = {}
# timing decorator
def measure_time(func):
    '''
    decorator for timing
    '''
    def wrapper(*arg, **kwargs):
        start_time = perf_counter()
        #result = func(*arg)
        result = func(*arg, **kwargs)

        # use the function name as the timer_count element
        if func.__name__ in timer_counter:
            timer_counter[func.__name__] += perf_counter() - start_time
        else:
            # create dict member as they are used
            timer_counter[func.__name__] = perf_counter() - start_time
        return result
    return wrapper


def old_convert_to_int(x):
    '''
    convert x to an int or pd.NA
    '''
    retval = None
    if isinstance(x, int):
        retval = x
    elif isinstance(x, float):
        if not math.isnan(x):
            retval = int(x)
        else:
            retval = pd.NA

    return retval

def convert_to_int(x):
    '''
    convert x to an int or pd.NA
    '''
    if pd.isna(x):
        return pd.NA
    return int(x)
