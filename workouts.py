# workouts.py
'''
naming
- functions named _report are called from run_suite.txt
- functions names _rpt are called from here
- consider refactoring with dataframe.apply() for reports e.g.
- x.com/i/grok/share/7ebc346c9fdb4911b866ef14e6cbf883
'''
# pylint exceptions
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=exec-used

#std
import calendar
from csv import reader
import datetime
from datetime import timedelta
#from decimal import *
import math
import sys
import warnings

# venv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tabulate

# config
from config import (
    get_config
)

# utility funcs
from utility import (
    get_num_workout_days,
    convert_to_mins,
    convert_date_to_unixdays,
    convert_date_to_week,
    convert_date,
    counter_report,
    convert_to_int,
    get_event,
    get_track_info,
    measure_time,
    timer_counter,
    unixday_now
    )


# configure pd
# pd.options.display.max_rows = 9999
pd.set_option('future.no_silent_downcasting', True)
pd.set_option('display.max_rows', 10000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 500)
# these don't work
#pd.set_option('display.na_rep', '')
#pd.options.display.na_rep = "Missing"

# pd.set_eng_float_format(accuracy=2, use_eng_prefix=True)

# warnings
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message=".*Mean of empty slice.*"   # matches the exact phrase
)


# globals
# constants
WORKOUT_EVENTS = ['bike', 'sbike', 'gym', 'walk']
MOVING_EVENTS = ['bike', 'walk']

# headings
STANDARD_RPT_DATA = ("bmi    bmin  bct    elev    bmph    bmax      cal   "
                     "sbmi  sbct     sbcal     "
                     "gct     "
                     "wmi   wmin   wct    elev    wmph    wmax      cal "
                     "|  miles count    min mdwt")
STANDARD_RPT_HEADING = f"year  mo     {STANDARD_RPT_DATA}"
STANDARD_RPT_HEADING_WK = f"year  wk     {STANDARD_RPT_DATA}"
INTERVAL_RPT_HEADING = f"Interval      {STANDARD_RPT_DATA}"

# just want 1-12. this is month # not how many months anything goes back
rpt_months = range(1, 13)

# just want 1-53. this is week # not how many weeks anything goes back
rpt_weeks = range(0, 54)

# get config file elements
config = get_config()

# populate config-based globals
RPT_YEARS = range(
    int(config['REPORT_YEAR_START']),
    datetime.datetime.now().year + 1
    )

# used in years_to_report_summary
YEARS_TO_REPORT=int(config['YEARS_TO_REPORT'])

LONG_RIDE_THRESHOLD = int(config['LONG_RIDE_THRESHOLD'])

def get_maint_event_data():
    '''
    read maint event data from file
    return dict of maint events
    '''
    # open the file using "with"
    # statement
    retval = {}
    maint_file = "maintenance.csv"
    with open(maint_file, 'r', encoding='utf-8') as data:
        for line in reader(data):
            # line 0 is column header, skip it
            if line[0] == 'event':
                continue
            # skip commented items
            if line[0][0] == "#":
                continue
            # create unixdays from the yr mo day data
            unix_days = convert_date_to_unixdays(
                datetime.datetime(
                    int(line[1]),
                    int(line[2]),
                    int(line[3])))
            # assign to dict
            retval[line[0]] = unix_days
            #print(line)
        #print (retval)
    return retval

def data_rpt(df_bike, df_sbike, df_gym, df_walk, date_str):
    '''
    provide the dfs and output as planned
    '''
    #print("data_rpt()")
    # rest is same as standard_rpt, perhaps make its own func?
    new_df_bike = df_bike[['Date', 'Miles', 'Time_Tot_Min', 'Elevi', 'Mph',
                           'Descr', 'Wt', 'Event', 'Cali']]
    new_df_sbike = df_sbike[['Date', 'Time_Tot_Min',
                           'Descr', 'Wt', 'Event', 'Cali']]
    new_df_gym = df_gym[['Date', 'Descr', 'Wt', 'Event']]
    new_df_walk = df_walk[['Date', 'Miles', 'Time_Tot_Min', 'Elevi', 'Mph',
                           'Descr', 'Wt', 'Event', 'Cali']]

    # show each event?
    # print (new_df_bike)

    # bike totals
    tot_miles = new_df_bike['Miles'].sum()
    count_events = new_df_bike['Miles'].count()
    tot_minutes = new_df_bike['Time_Tot_Min'].sum()
    tot_elev = new_df_bike['Elevi'].sum()
    mean_mph = new_df_bike['Mph'].mean()
    max_mph = new_df_bike['Mph'].max()
    tot_cali = new_df_bike['Cali'].sum()

    # string output
    rpt_bike = f"{tot_miles:{6}.{1}f}  {tot_minutes:{5}.{0}f}   "
    rpt_bike += f"{count_events:{3}d}  {tot_elev:{6}}   {mean_mph:{5}.{1}f}   "
    rpt_bike += f"{max_mph:{5}.{1}f}  {tot_cali:{7}d}"

    tot_bike = [tot_miles, count_events, tot_minutes, tot_cali]

    # sbike totals
    #tot_miles = new_df_sbike['Miles'].sum()
    tot_miles = 0
    count_events = new_df_sbike['Date'].count()
    tot_minutes = new_df_sbike['Time_Tot_Min'].sum()
    tot_elev = 0
    mean_mph = 0
    max_mph = 0
    tot_cali = new_df_sbike['Cali'].sum()

    # string output
    rpt_sbike = f"{tot_minutes:{5}.{0}f}   "
    rpt_sbike += f"{count_events:{3}d}   "
    rpt_sbike += f"{tot_cali:{7}d}   "

    tot_sbike = [tot_miles, count_events, tot_minutes, tot_cali]

    # gym totals
    #tot_miles = new_df_walk['Miles'].sum()
    count_events = new_df_gym['Date'].count()
    #tot_minutes = new_df_walk['Time_Tot_Min'].sum()
    #tot_elev = new_df_walk['Elevi'].sum()
    #mean_mph = new_df_walk['Mph'].mean()
    #max_mph = new_df_walk['Mph'].max()
    #tot_calories = new_df_walk['Calories'].sum()

    # string output
    rpt_gym = f"{count_events:{3}d}"

    # make compatible with the other tot vars above
    # not used
    #tot_gym = [0, count_events, 0, 0]

    # walk totals
    tot_miles = new_df_walk['Miles'].sum()
    count_events = new_df_walk['Miles'].count()
    tot_minutes = new_df_walk['Time_Tot_Min'].sum()
    tot_elev = new_df_walk['Elevi'].sum()
    mean_mph = new_df_walk['Mph'].mean()
    max_mph = new_df_walk['Mph'].max()
    tot_cali = new_df_walk['Cali'].sum()

    # string output
    rpt_walk = f"{tot_miles:{6}.{1}f}  {tot_minutes:{5}.{0}f}   "
    rpt_walk += f"{count_events:{3}d}  {tot_elev:{6}}   {mean_mph:{5}.{1}f}   "
    rpt_walk += f"{max_mph:{5}.{1}f}  {tot_cali:{7}d}"

    tot_walk = [    tot_miles, count_events, tot_minutes, tot_cali]

    # is this relevant? maybe omit miles?
    # totals for all
    tot_miles = tot_bike[0] + tot_walk[0]
    #tot_count = tot_bike[1] + tot_walk[1] + tot_gym[1]
    tot_count = tot_bike[1] + tot_sbike[1] + tot_walk[1]
    tot_minutes = tot_bike[2] + tot_sbike[2] + tot_walk[2]
    # not used
    #tot_calories = tot_bike[3] + tot_walk[3]

    # median weight
    combined_df = pd.concat([new_df_bike, new_df_sbike, new_df_gym, new_df_walk])
    # median_weight = int(combined_df['Wt'].median())
    median_weight = round(combined_df['Wt'].median(), 0)

    rpt_all = f"{tot_miles:{6}.{1}f}   {tot_count:{3}d}  {tot_minutes:{5}.{0}f}  "
    rpt_all += f"{median_weight:{3}.{0}f}"

    print(f"{date_str}   {rpt_bike}  {rpt_sbike}  {rpt_gym}  {rpt_walk} | {rpt_all}")


def standard_rpt(df, year, month=None, week=None, interval=None):
    '''
    # month/week detail and year totals are the same except for the df's
    # return the count of events
    '''
    # if month is None, different handling
    df_bike = None
    df_sbike = None
    df_gym = None
    df_walk = None
    day_cutoff = None
    tot_count = 0

    # make date_str
    if month is not None:
        date_str = f"{year} {month:2d}"
    elif week is not None:
        date_str = f"{year} {week:2d}"
    elif interval is not None:
        date_str = f"Last {interval:3d}"
        unixdays = unixday_now()
        day_cutoff = unixdays - interval
    else:
        date_str = f"{str(year):7s}"

    # create df's based upon whether month is provided
    if month is not None:
        df_bike = df[
            (df.Date_year == year) &
            (df.Date_month == month) &
            (df.Event == "bike")  # &
            ]
        df_sbike = df[
            (df.Date_year == year) &
            (df.Date_month == month) &
            (df.Event == "sbike")  # &
            ]
        df_gym = df[
            (df.Date_year == year) &
            (df.Date_month == month) &
            (df.Event == "gym")  # &
            ]
        df_walk = df[
            (df.Date_year == year) &
            (df.Date_month == month) &
            (df.Event == "walk")  # &
            ]
    elif week is not None:
        df_bike = df[
            (df.Date_year == year) &
            (df.Date_week == week) &
            (df.Event == "bike")  # &
            ]
        df_sbike = df[
            (df.Date_year == year) &
            (df.Date_week == week) &
            (df.Event == "sbike")  # &
            ]
        df_gym = df[
            (df.Date_year == year) &
            (df.Date_week == week) &
            (df.Event == "gym")  # &
            ]
        df_walk = df[
            (df.Date_year == year) &
            (df.Date_week == week) &
            (df.Event == "walk")  # &
            ]
    elif interval is not None:
        df_bike = df[
            (df.Date_unixdays >= day_cutoff) &
            (df.Event == "bike")  # &
            ]
        df_sbike = df[
            (df.Date_unixdays >= day_cutoff) &
            (df.Event == "sbike")  # &
            ]
        df_gym = df[
            (df.Date_unixdays >= day_cutoff) &
            (df.Event == "gym")  # &
            ]
        df_walk = df[
            (df.Date_unixdays >= day_cutoff) &
            (df.Event == "walk")  # &
            ]
    else:
        df_bike = df[
            (df.Date_year == year) &
            (df.Event == "bike")  # &
            ]
        df_sbike = df[
            (df.Date_year == year) &
            (df.Event == "sbike")  # &
            ]
        df_gym = df[
            (df.Date_year == year) &
            (df.Event == "gym")  # &
            ]

        df_walk = df[
            (df.Date_year == year) &
            (df.Event == "walk")  # &
            ]

    # do not print if there are no records
    # if len(df.index) > 0:
    lx = len(df_bike.index) + len(df_gym.index) + len(df_walk.index)
    if lx == 0:
        return tot_count

    new_df_bike = df_bike[['Date', 'Miles', 'Time_Tot_Min', 'Elevi', 'Mph',
                           'Descr', 'Wt', 'Cali', 'Event']]
    new_df_sbike = df_sbike[['Date', 'Time_Tot_Min',
                           'Descr', 'Wt', 'Cali', 'Event']]
    new_df_gym = df_gym[['Date', 'Descr', 'Wt', 'Event']]
    new_df_walk = df_walk[['Date', 'Miles', 'Time_Tot_Min', 'Elevi', 'Mph',
                           'Descr', 'Wt', 'Cali', 'Event']]

    data_rpt(new_df_bike, new_df_sbike, new_df_gym, new_df_walk, date_str)
    # print (newdf1)

    # still need total_count retval
    # exclude gym number from total count
    #tot_count = new_df_bike['Miles'].count() +
    # new_df_gym['Date'].count() +
    # new_df_walk['Miles'].count()
    # use 'Date' instead of 'Miles'
    tot_count = new_df_bike['Date'].count() + \
        new_df_sbike['Date'].count() + \
        new_df_walk['Date'].count()

    # return the number of events
    return tot_count


def ytd_total_rpt(df, date_str, year, day_of_year):
    '''
    ytd_total_rpt(df, date_str, _year, day_of_year)
    '''
    # if month is None, different handling
    df_bike = None
    df_sbike = None
    df_walk = None

    # create df's based upon whether month is provided
    df_bike = df[
        (df.Date_year == float(year)) &
        (df.Date_doy <= float(day_of_year)) &
        (df.Event == "bike")  # &
        ]

    # print(df_bike.info())

    df_sbike = df[
        (df.Date_year == float(year)) &
        (df.Date_doy <= float(day_of_year)) &
        (df.Event == "sbike")  # &
        ]

    df_walk = df[
        (df.Date_year == float(year)) &
        (df.Date_doy <= float(day_of_year)) &
        (df.Event == "walk")  # &
        ]

    df_gym = df[
        (df.Date_year == float(year)) &
        (df.Date_doy <= float(day_of_year)) &
        (df.Event == "gym")  # &
        ]

    # rest is same as standard_rpt, perhaps make its own func?
    new_df_bike = df_bike[['Date', 'Miles', 'Time_Tot_Min', 'Elevi', 'Mph',
                           'Descr', 'Wt', 'Event', 'Cali']]
    # Miles, Elivi, Mph not valid data here
    new_df_sbike = df_sbike[['Date', 'Miles', 'Time_Tot_Min', 'Elevi', 'Mph',
                           'Descr', 'Wt', 'Event', 'Cali']]
    new_df_gym = df_gym[['Date', 'Descr', 'Wt', 'Event']]
    new_df_walk = df_walk[['Date', 'Miles', 'Time_Tot_Min', 'Elevi', 'Mph',
                           'Descr', 'Wt', 'Event', 'Cali']]

    data_rpt(new_df_bike, new_df_sbike, new_df_gym, new_df_walk, date_str)

def wt_rpt(df, date_str, year, month=None):
    '''
    # show avg, min, max weight per month
    # month detail and year totals are the same except for the df's
    '''
    # if month is None, different handling
    #df_bike = None
    #df_walk = None

    # create df's based upon whether month is provided
    if not month:
        df_wt = df[
            (df.Date_year == year)
            ]
    else:
        df_wt = df[
            (df.Date_year == year) &
            (df.Date_month == month)
            ]

    # do not print if there are no records
    # if len(df.index) > 0:
    lx = len(df_wt.index)
    if lx == 0:
        return

    # bike totals
    mean_wt = df_wt['Wt'].mean()
    median_wt = df_wt['Wt'].median()
    min_wt = df_wt['Wt'].min()
    max_wt = df_wt['Wt'].max()
    rpt_wt = f"{min_wt:{6}.{0}f} {mean_wt:{6}.{1}f} "\
    f"{median_wt:{6}.{0}f} {max_wt:{6}.{0}f} "

    print(f"{date_str}   {rpt_wt}")


def totals_report(df, event):
    '''
    totals for the df, varies by event
    '''
    print("totals_report()")

    # statistical stuff
    # cols desired
    #stat_columns = [
    #    'Miles',
    #    'Elevi',
    #    'Time_Tot_Min',
    #    'Rest_60_Min',
    #    'Mph',
    #    'Grade',
    #    'VAMi',
    #    'Cali',
    #    'FB_Pi',
    #    'FB_Vi',
    #    'FB_Mi',
    #    'FB_Li',
    #    'FB_AVGi',
    #    'FB_CLi']
    #desc = df[stat_columns].describe()
    #desc.loc['median'] = df[stat_columns].median()

    # how to get median? need to specify the fields again?
    #desc = df.describe()
    #desc.loc['median'] = df.median()
    #desc = desc.round(1)

    #print(desc)
    #return

    # bike, walk
    if event in MOVING_EVENTS:
        print(f"sum miles: {df['Miles'].sum():.2f}")
        print(f"count events: {df['Miles'].count()}")

        # using describe
        #stat_columns = ['Miles']
        #desc = df[stat_columns].describe()
        #desc.loc['sum'] = df[stat_columns].sum()
        #desc = desc.round(1)
        #print (desc)

    # gym
    if event == "gym":
        print(f"count events: {df['Date'].count()}")

    if event == 'bike':
        #print(f"sum elev: {df['Elevi'].sum():.0f}")
        print(f"median elev: {df['Elevi'].median():.0f}")

        # using describe
        #stat_columns = ['Elevi']
        #desc = df[stat_columns].describe()
        #desc.loc['sum'] = df[stat_columns].sum()
        #desc = desc.round(0)
        #print (desc)

    if event in MOVING_EVENTS:
        #print(f"mean tot time min: {df['Time_Tot_Min'].mean():.02f}")
        #print(f"median tot time min: {df['Time_Tot_Min'].median():.02f}")
        #print(f"min tot time min: {df['Time_Tot_Min'].min():.02f}")
        pass

    if event == 'bike':
        print(f"median rest_60 min: {df['Rest_60_Min'].median():.02f}")

    if event in MOVING_EVENTS:
        #print(f"mean mph: {df['Mph'].mean():.01f}")
        #print(f"median mph: {df['Mph'].median():.01f}")
        #print(f"max mph: {df['Mph'].max():.01f}")
        pass

    if event == 'bike':
        #print(f"mean asc_desc: {df['Asc_Desc'].mean():.01f}")
        #print(f"mean grade: {df['Grade'].mean():.01f}")
        #print(f"mean VAMi: {df['VAMi'].mean():.01f}")
        #print(f"median asc_desc: {df['Asc_Desc'].median():.0f}")
        #print(f"median grade: {df['Grade'].median():.0f}")
        #print(f"median VAMi: {df['VAMi'].median():.0f}")
        pass

    # all events
    #print(f"mean FB_CLi: {df['FB_CLi'].mean():.01f}")
    # not all events have this data so check to avoid runtime error
    if len(df['Cali']) > 0:
        #print(f"median Cali: {df['Cali'].median():.0f}")
        pass

        # using describe
        #stat_columns = ['Cali']
        #desc = df[stat_columns].describe()
        #desc.loc['sum'] = df[stat_columns].sum()
        #desc = desc.round(0)
        #print (desc)

    # for just FB_CLi
    if len(df['FB_CLi']) > 0:
        #print(f"median FB_AVGi: {df['FB_AVGi'].median():3.0f}")
        #print(f"median FB_CLi:  {df['FB_CLi'].median():3.0f}")
        #print(f"median FB_Ri:  {df['FB_Ri'].median():3.0f}")
        pass

    # for all FB data
    # HEREHERE figure out how to get the call to ignore the records where this data doesn't exist
    fb_columns = [
        'Asc_Desc',
        'Grade',
        'Mph',
        'Time_Tot_Min',
        'VAMi',
        'FB_Pi',
        'FB_Vi',
        'FB_Mi',
        'FB_Li',
        'FB_AVGi',
        'FB_CLi',
        'FB_RHRi',
        'FB_HRVi',
        'FB_Ri',
        'FB_HRV_NEXTi'
        ]

    for _fb_column in fb_columns:
        #if len(df[_fb_column]) > 0 and not df[_fb_column].isna().any():
        if _fb_column in df.columns:
            if len(df[_fb_column]) > 0:
                #print(f"median {_fb_column}: {df[_fb_column].median():.0f}")
                #median = df[_fb_column].median()
                #std = df[_fb_column].std()

                # providing quantiles is better than median/std
                q25 = df[_fb_column].quantile(0.25)
                q50 = df[_fb_column].quantile(0.50)
                q75 = df[_fb_column].quantile(0.75)
                vmin = float(df[_fb_column].min())
                vmax = float(df[_fb_column].max())

                # different for mph
                if _fb_column in ['Asc_Desc','Grade','Mph']:
                    print(f"{_fb_column:<13} "
                        f"q25/50/75: {q25:3.1f}/{q50:3.1f}/{q75:3.1f} "
                        f"min/max: {vmin:3.1f}/{vmax:3.1f}"
                    )
                else:
                    print(f"{_fb_column:<13} "
                        f"q25/50/75: {q25:3.0f}/{q50:3.0f}/{q75:3.0f} "
                        f"min/max: {vmin:3.0f}/{vmax:3.0f}"
                    )

    print(" ")

# these are reports that are called directly by main()
def event_report(df, event, rider=None, threshold=0):
    '''
    #########################################################
    # bike route report
    # enhanced to support gym and walk events
    # all rides last 365 day year in date order
    # try out a total
    # https://www.listendata.com/2019/07/how-to-filter-pandas-dataframe.html
    # https://www.listendata.com/2019/06/pandas-drop-columns-from-dataframe.html
    # add extra day to make sure to get today's items
    '''
    #print(f"calling event_report() for {event}")
    unix_days_now = unixday_now()
    unix_days_range = unix_days_now - 4*365 #HEREHERE

    newdf = None
    if rider:
        newdf = df[
            (df.Event == event) &
            (df.Date_unixdays > unix_days_range) &
            (df.Pat == "x") &
            (df.Miles >= threshold)
            ]
    #else:
        # Miles is not populated for gym
        # maybe just use event?
        #newdf = df[
        #    (df.Event == event) &
        #    (df.Date_unixdays > unix_days_range) &
        #    (df.Miles >= threshold)
        #    ]
    # miles not relevant for gym
    elif event == 'gym':
        newdf = df[
            (df.Event == event) &
            (df.Date_unixdays > unix_days_range)
            ]
    else:
        newdf = df[
            (df.Event == event) &
            (df.Date_unixdays > unix_days_range) &
            (df.Miles >= threshold)
            ]

    # print (newdf)

    # pick columns based upon event, need this so the print statement has what we want
    if event == 'bike':
        # Added Year to use in totals_report for bike rides
        newdf1 = newdf[['Year', 'Date', 'Time_Tot_Min', 'Rest_60_Min',
                        'Miles', 'Elevi', 'Mph', 'Asc_Desc', 'Grade',
                        'VAMi', 'Cali', 'Weather', 
                        'FB_Pi','FB_Vi','FB_Mi',
                        'FB_Li','FB_AVGi','FB_CLi',
                        'FB_RHRi','FB_HRVi','FB_Ri','FB_HRV_NEXTi',
                        'Descr']]
    elif event == 'gym':
        newdf1 = newdf[['Date', 'Time_Tot_Min',
                        'Cali',
                        'FB_Pi','FB_Vi','FB_Mi',
                        'FB_Li','FB_AVGi','FB_CLi',
                        'FB_RHRi','FB_HRVi','FB_Ri','FB_HRV_NEXTi',
                        'Descr']]
    else: # default event is walk
        newdf1 = newdf[['Date', 'Time_Tot_Min',
                        'Miles', 'Mph', 'Grade',
                        'Cali', 'Weather', 
                        'FB_Pi','FB_Vi','FB_Mi',
                        'FB_Li','FB_AVGi','FB_CLi',
                        'FB_RHRi','FB_HRVi','FB_Ri','FB_HRV_NEXTi',
                        'Descr']]

    print(" ")
    print("begin event_report()")
    # HEREHERE 365 should not be hard-coded, check the df?
    print(f"Last 365 Days {event.title()} by Date, {rider} threshold {threshold}")
    # replace <NA> with '' just useful for the print _df statement
    # deprecated _df = newdf1.fillna('').infer_objects(copy=False)
    _df = newdf1.fillna('').infer_objects()
    #print(newdf1.fillna('').infer_objects(copy=False))

    # omit Year if the field exists before listing/printing the df
    print_df = _df.drop(columns=['Year'], errors='ignore')

    # print the whole df
    # but a long list won't havecolumn names in view
    #print(print_df.to_string(index=False))

    # so...
    # 1. print all but the last row..
    print(print_df.iloc[:-1].to_string(index=False))

    # 2. print the last row
    print() # blank line
    print(print_df.tail(1).to_string(index=False))

    # totals_report for all events
    totals_report(newdf1, event)
    # iterate through years and do totals_report for each year
    # not all events have Year
    if 'Year' in newdf1.columns:
        totals_years = sorted(newdf1['Year'].astype(int).unique())

        # do totals_report() for individual years if there is more than 1 year in the list
        if len(totals_years) > 1:
            print(f"totals_years {totals_years}")
            for _y in reversed(totals_years):
                print(f"Totals for {_y}:")
                totals_report(newdf1[newdf1['Year'] == _y], event)
                # paradigm df[df['column_name'] == value]

    print("end event_report()")
    return newdf1


@measure_time
def unique_route_report(df, event):
    '''
    takes supplied df and reports on unique routes
    #########################################################
    # unique route report
    # get all unique descr in a list
    '''
    print(f"calling unique_route_report() for {event}")
    unique_descr = df.Descr.unique().tolist()
    unique_descr.sort()
    print(f"unique descr: {unique_descr}")

    # loop through the list
    print("Last 365 Day by Route")
    for _descr in unique_descr:
        _df = df[
            (df.Descr == _descr)
            ]

        # pick fields based upon event type
        if event == 'bike':
            # added Year for totals_report
            _newdf = _df[['Year', 'Date', 'Time_Tot_Min', 'Rest_60_Min',
                          'Miles', 'Elevi', 'Mph', 'Asc_Desc',
                          'Grade', 'VAMi', 'Cali', 'Weather',
                          'FB_Pi','FB_Vi','FB_Mi',
                          'FB_Li','FB_AVGi','FB_CLi',
                          'FB_RHRi','FB_HRVi','FB_Ri','FB_HRV_NEXTi',
                          'Descr']]
        elif event == 'gym':
            _newdf = _df[['Date', 'Time_Tot_Min',
                          'Cali',
                          'FB_Pi','FB_Vi','FB_Mi',
                          'FB_Li','FB_AVGi','FB_CLi',
                          'FB_RHRi','FB_HRVi','FB_Ri','FB_HRV_NEXTi',
                          'Descr']]

        else:
            _newdf = _df[['Date', 'Time_Tot_Min', 'Miles', 'Mph',
                          'Cali', 'Weather', 
                          'FB_Pi','FB_Vi','FB_Mi',
                          'FB_Li','FB_AVGi','FB_CLi',
                          'FB_RHRi','FB_HRVi','FB_Ri','FB_HRV_NEXTi',
                          'Descr']]

        #print(_newdf)
        #print(_newdf.fillna(''))
        #print(_newdf.fillna('').infer_objects(copy=False))
        
        # deprecated _df = _newdf.fillna('').infer_objects(copy=False)
        _df = _newdf.fillna('').infer_objects()

        # how many rows in _df
        num_rows = len(_df)
        # if more than 20 print so column titles are before the last row
        if num_rows > 20:
            # so...
            # 1. print all but the last row..
            print(_df.iloc[:-1].to_string(index=False))

            # 2. print the last row
            print() # blank line
            print(_df.tail(1).to_string(index=False))
        else:
            print(_df.to_string(index=False))

        # totals
        totals_report(_newdf, event)

        # totals for individual years for bike events
        if event == 'bike':
            # Get the years for the _newdf and do the totals for each year
            #totals_years = list(range(_newdf['Year'].min(), _newdf['Year'].max() + 1))
            totals_years = sorted(_newdf['Year'].astype(int).unique())
            #totals_years = df['Year'].unique().astype(int).tolist()

            # do totals_report() for individual years if there is more than 1 year in the list
            if len(totals_years) > 1:
                print(f"totals_years {totals_years}")
                for _y in reversed(totals_years):
                    print(f"Totals for {_y}:")
                    totals_report(_newdf[_newdf['Year'] == _y], event)
                    # paradigm df[df['column_name'] == value]



@measure_time
def years_to_report_summary(df):
    '''
    # create a list using range and YEARS_TO_REPORT
    # need to make a df that has the records of interest
    '''
    print("============================")
    print("Years to Report Summary")

    unix_days_now = unixday_now()
    unix_days_now += 1

    # first day of YEARS_TO_REPORT years ago
    year_of_now = datetime.datetime.now().year
    date_start = datetime.datetime(year_of_now - YEARS_TO_REPORT, 1, 1)
    unix_date_start = convert_date_to_unixdays(date_start)

    #rpt_days = range(unix_days_14,  unix_days_now)
    rpt_days = range(unix_date_start,  unix_days_now)
    # print (rpt_days)

    # template df with df columns
    newdf = pd.DataFrame(columns=list(df))

    # loop through rows
    # new_index = 0
    years = []
    for index, row in df.iterrows():
        this_unixday = df.loc[index, 'Date_unixdays']
        if this_unixday in rpt_days:
            # entry = df.loc[index]
            # newdf= pd.concat([newdf,entry])

            # add the row
            # Add records to dataframe using the .loc function
            # print (row)
            newdf.loc[len(newdf), :] = row

            # pd.concat([newdf, row.to_frame().T], ignore_index=True)

            # pd.concat([newdf, row], ignore_index=True)
            # newdf = pd.concat([newdf,row])
            # newdf.loc[new_index] = row
            #
            # new_index += 1

            # update the years index
            if df.loc[index]['Date_year'] not in years:
                years.append(int(df.loc[index]['Date_year']))
    # print (newdf)

    # play around with plotting
    # newdf.plot(kind = 'scatter', y = 'Miles', x = 'Date_unixdays')

    # newdf.info()
    # newdf.plot(kind = 'scatter', y = 'Mph', x = 'Date_unixdays')
    # plt.show()
    # newdf.plot(kind = 'scatter', y = 'Time_Tot_Min', x = 'Date_unixdays')
    # newdf.plot(kind = 'scatter', y = 'Time_Tot_Min', x = 'Date_month')
    # plt.show()

    # standard report
    # next- look at year-month totals and year totals

    for _year in years:
        print(STANDARD_RPT_HEADING)
        for _month in rpt_months:

            # see if this unixday is in the range
            this_unixday = convert_date_to_unixdays(
                datetime.datetime(_year, _month, 1))
            if this_unixday not in rpt_days:
                continue

            standard_rpt(newdf, _year, month=_month)

        # year total
        # only for current year
        if _year == years[-1]:
            standard_rpt(newdf, _year)

        print(" ")

    return newdf

@measure_time
def read_raw_data(filename):
    '''
    read raw data, return dataframe object
    '''
    # load data into a DataFrame object:
    # all subsequent reports use this as a basis
    df = pd.read_csv(filename)
    return df

@measure_time
def workout_operation(row, weights):
    '''
    go through raw data and set new rows
    also populate weights dict
    use df.apply() function like this
    games_df[
        [
        "game_date",
        "date_year_week",
        "p_visitor_shots_diff",
        "p_visitor_goals_diff",
        "p_home_shots_diff",
        "p_home_goals_diff",
        "p_result_2pt",
        "p_result_10pt",
        "p_margin_diff",
        "p_total_diff"
        ]
        ] = games_df.apply(games_operation,
                    axis=1,
                    league_totals=league_totals,
                    teams=teams,
                    relevant_date=relevant_date)
        from nhl.games.py:games_operation() func- see game.py in this dir
    '''
    # return if game is not yet played and date is > today
    # paradigm for retval
    #retval = pd.Series ( {
    #    "game_date": game_date,
    #    "date_year_week": date_year_week,
    #    "p_visitor_shots_diff": np.nan,
    #    "p_visitor_goals_diff": np.nan,
    #    "p_home_shots_diff": np.nan,
    #    "p_home_goals_diff": np.nan,
    #    "p_result_2pt": np.nan,
    #    "p_result_10pt": np.nan,
    #    "p_margin_diff": np.nan,
    #    "p_total_diff": np.nan
    #})

    # process row data- convert date stuff to ints
    # consider moving this to the calling function and converting the whole dataframe at once
    row[["Year", "Month", "Day"]] = row[["Year", "Month", "Day"]].astype("Int64")

    date_year = None
    date_month = None
    date_dom = None
    try:
        date_year = row["Year"]
        date_month = row["Month"]
        date_dom = row["Day"]
    except TypeError as e1:
        print (e1)
        print (row)


    # old df had DATE, which would actually be handy-- yyyy/mm/dd
    date_str = None
    date = None
    try:
        date_str = f'{row["Year"]:04}/{row["Month"]:02}/{row["Day"]:02}'
        date = str(date_str)
    # just in case something is weird here
    # pylint: disable=bare-except,broad-exception-caught
    except Exception as e:
        print(f"hey, exception! {e}")
        print (row)

    # compute doy from python datetime obj
    try:
        date_doy = int(
            datetime.date(row["Year"],
            row["Month"],
            row["Day"]).timetuple()[7]
            )
    except TypeError as e:
        print (e)
        print (row)

    date_unixdays = convert_date_to_unixdays(
        datetime.datetime(row["Year"],
                            row["Month"],
                            row["Day"])
        )

    # add week of year
    date_week = convert_date_to_week(
        datetime.datetime(row["Year"],
                            row["Month"],
                            row["Day"])
        )

    # calories
    cali = convert_to_int(row['Cal'])

    # VAM- make it an int
    vami = convert_to_int(row['VAM'])

    # format wt- could be blank, in which case it's a float nan
    # but we'd like it to be an int- pd.NA is a float so convert
    # to int but you can't do that
    # so even though wt is an int, make it a float in the df
    wt = row['Wt']
    if isinstance(wt, str):
        wt = wt.strip()
        if len(wt) > 0:
            wt = float(wt)
        else:
            wt = pd.NA
    else:
        wt = pd.NA

    # weight checker
    # simplified from earlier version, not sure it will work though
    # if this weight is in weights, update the date
    # if not, add it
    if not pd.isna(wt):
        if wt in weights:
            # update 2nd element
            weights[wt] = (weights[wt][0],date_str)
        else:
            # define tuple
            weights[wt] = (date_str,0)

    # times
    time_tot = row['Time_Tot']
    time_tot_min = pd.NA
    asc_min = pd.NA
    desc_min = pd.NA
    asc_desc = pd.NA
    # some events have asc/desc, others have time tot only
    # do we have total time? convert to minutes if we do. it's in hh:mi:ss format as a string
    # if we don't have total time, we'll might have time_asc, time_desc
    if isinstance(time_tot, str):
        time_tot_min = convert_to_mins(time_tot)
    else:
        asc_min = convert_to_mins(row['Time_Asc'])
        desc_min = convert_to_mins(row['Time_Desc'])
        time_tot_min = asc_min + desc_min
        if desc_min > 0:
            asc_desc = round(asc_min/desc_min, 2) # ratio

    # time stop, rest_60 calculation
    time_stop = row['Time_Stop']
    rest_60_min = pd.NA
    # compute if it's a str, if empty it will be a float nan
    if isinstance(time_stop, str):
        time_stop_min = convert_to_mins(time_stop)

        if time_stop_min > 0:
            rest_60_min = (float)(60) * time_stop_min / time_tot_min
            if not pd.isna(rest_60_min):
                rest_60_min = round(rest_60_min,2)
                # use Decimal to fix the 100ths? does not work

    # weather- no handling, it should be in the final df anyway?

    # stuff
    miles = row['Miles']
    # recompute miles, sec_per_lap if laps
    # some walking isn't laps, just use raw app/gps miles for those
    laps = row['Laps']
    sec_per_lap = pd.NA
    descr = str(row['Descr']).lower()

    # compute if laps are specified
    if not math.isnan(laps):
        descr = str(row['Descr']).lower()
        track_info = get_track_info(
            descr,
            time_tot_min,
            laps
            )

        sec_per_lap = track_info['sec_per_lap']
        miles = track_info['track_miles']


    # need miles to calculate event type
    # miles might be in raw data or might be calculated if at track
    #if row["Miles"] != df.loc[index, 'Miles']:
    #    print(f"{date_str} {df.loc[index, 'Miles']} {row['Miles']}")

    #miles = df.loc[index, 'Miles']
    this_event = get_event(miles, descr)
    # if event is bike from stationary bike, miles will still be nan.
    # set to 0 to make the filter match better later
    if 'bike' in this_event and math.isnan(row['Miles']):
        miles = 0

    # compute Elev- want to be an int
    elevi = convert_to_int(row['Elev'])

    # compute mph
    mph = pd.NA
    if not pd.isna(time_tot_min):
        if time_tot_min > 0:
            mph = round((float)(60) * miles / time_tot_min,1)

            # float(f"{mph:.1f}")

    # compute grade
    grade = pd.NA
    elev_feet = float((100 * row['Elev']))
    if not pd.isna(miles):
        half_trip_feet = float((miles/2)*5280)

        if half_trip_feet > 0:
            grade = round(elev_feet / half_trip_feet,1)

    # fitbit
    # convert fitbit elements to ints
    # these are raw col names, append "i" for the int values
    fb_elements = [
        'FB_P',
        'FB_V',
        'FB_M',
        'FB_L',
        'FB_AVG',
        'FB_CL',
        'FB_RHR',
        'FB_HRV',
        'FB_R',
        'FB_HRV_NEXT',
    ]
    fb_data = {}
    for _e in fb_elements:
        _e_raw = row[_e]
        _ei = _e + "i" # integer value name
        # convert float to int
        ei = convert_to_int(row[_e])
        fb_data[_ei] = ei

    # return the new columns needed
    retval = pd.Series ( {
        'Date_year': date_year,
        'Date_month': date_month,
        'Date_dom': date_dom,
        'Date_doy': date_doy,
        'Date': date, # date str 
        'Date_unixdays': date_unixdays,
        'Date_week': date_week,
        # convert to int
        'Cali':cali, # rename to Cali which is Cal + i for int
        'VAMi': vami,
        'Wt': wt,
        'Time_Tot_Min': time_tot_min,
        'Time_Asc_Min': asc_min,
        'Time_Desc_Min': desc_min,
        'Asc_Desc': asc_desc,
        'Rest_60_Min': rest_60_min,
        'Sec_per_lap': sec_per_lap,
        'Miles': miles,
        'Descr': descr,
        'Event': this_event,
        'Elevi': elevi,
        'Mph': mph,
        'Grade': grade,
        # fitbit int elements
        'FB_Pi': fb_data['FB_Pi'],
        'FB_Vi': fb_data['FB_Vi'],
        'FB_Mi': fb_data['FB_Mi'],
        'FB_Li': fb_data['FB_Li'],
        'FB_AVGi': fb_data['FB_AVGi'],
        'FB_CLi': fb_data['FB_CLi'],
        'FB_RHRi': fb_data['FB_RHRi'],
        'FB_HRVi': fb_data['FB_HRVi'],
        'FB_Ri': fb_data['FB_Ri'],
        'FB_HRV_NEXTi': fb_data['FB_HRV_NEXTi'],
    } )
    return retval


@measure_time
def process_df(df, weights):
    '''
    use apply function
    use df.apply() function like this
    games_df[
        [
        "game_date",
        "date_year_week",
        "p_visitor_shots_diff",
        "p_visitor_goals_diff",
        "p_home_shots_diff",
        "p_home_goals_diff",
        "p_result_2pt",
        "p_result_10pt",
        "p_margin_diff",
        "p_total_diff"
        ]
        ] = games_df.apply(games_operation,
                    axis=1,
                    league_totals=league_totals,
                    teams=teams,
                    relevant_date=relevant_date)
        from nhl.games.py:games_operation() func- see game.py in this dir

    '''
    # adding new columns to df
    df[
        [
        'Date_year',
        'Date_month',
        'Date_dom',
        'Date_doy',
        'Date', 
        'Date_unixdays',
        'Date_week',
        'Cali',
        'VAMi',
        'Wt',
        'Time_Tot_Min',
        'Time_Asc_Min',
        'Time_Desc_Min',
        'Asc_Desc',
        'Rest_60_Min',
        'Sec_per_lap',
        'Miles',
        'Descr',
        'Event',
        'Elevi',
        'Mph',
        'Grade',
        'FB_Pi',
        'FB_Vi',
        'FB_Mi',
        'FB_Li',
        'FB_AVGi',
        'FB_CLi',
        'FB_RHRi',
        'FB_HRVi',
        'FB_Ri',
        'FB_HRV_NEXTi'
        ]
    ] = df.apply(workout_operation,
                axis=1,
                weights=weights,
                # addl parameters for workout_operation if eneded
                )
    return df


@measure_time
def pat_events(df):
    '''
    # basic event report
    # pat's events
    '''
    _event = 'bike'
    # pat events- make an arg?
    df1 = event_report(df, event=_event, rider='pat')  # pat's rides
    unique_route_report(df1, event=_event)


@measure_time
def john_events(df):
    '''
    special output for john's events
    '''
    for _event in WORKOUT_EVENTS:
        df1 = event_report(df, event=_event)
        unique_route_report(df1, event=_event)

        # long events
        if _event == 'bike':
            df1 = event_report(df, event=_event, threshold=LONG_RIDE_THRESHOLD)
            unique_route_report(df1, event=_event)

@measure_time
def year_month_report(df):
    '''
    year month report
    '''
    print("Standard Report")
    print("============================")
    print(STANDARD_RPT_HEADING)
    for _year in RPT_YEARS:

        # month data just for current year?
        if _year == RPT_YEARS[-1]:
            print(" ")
            print(STANDARD_RPT_HEADING)
            for _month in rpt_months:
                standard_rpt(df, _year, month=_month)

        standard_rpt(df, _year)

    print(" ")


@measure_time
def year_month_grid_report(df):
    '''
    year month grid report
    report number of miles in year/month in grid format to allow comparison
    '''
    print("Year Month Grid Report")
    print("============================")
    # gather all years that have any bike miles
    # would be nice to have 2015 in config somewhere?

    def get_cell_string(count, miles):
        '''
        return the formatted cell contents for the count-miles data
        '''
        return f"{count:4.0f}-{miles:5.0f}"


    # might need other criteria?
    dff = df[
        (df['Event'] == 'bike') &
        #(df['Pat'].isna()) &
        # if i include this, it omits rides where pat rode also.
        # if 1, pat's rides only
        (df['Year'] >= int(config['REPORT_YEAR_START']))
        ]

    # grab data from the df to make the report
    miles_total = (dff[dff['Event'] == 'bike'].groupby(
        ['Year', 'Month','Event'])['Miles'].sum().reset_index(name='miles')
        )

    count_total = (df[df['Event'] == 'bike'].groupby(
        ['Year', 'Month','Event'])['Miles'].count().reset_index(name='count')
        )

    # merge into a single df
    result = pd.merge(miles_total, count_total, on=['Year', 'Month', 'Event'], how='left')
    #print (result)

    # get month totals- this will be the last row of the report
    # month miles
    total_data = {"Year": "All"}
    grand_total_count = 0
    grand_total_miles = 0
    for _month in range(1,13):

        # tuple of result instead
        count_miles = tuple(result.loc[result['Month'] == _month, ['count', 'miles']].sum())
        _cell_data = get_cell_string(count_miles[0], count_miles[1])

        # make the dataframe for the totals
        total_data[calendar.month_abbr[_month]] = _cell_data

        # add up for later use
        grand_total_count += count_miles[0]
        grand_total_miles += count_miles[1]

    # add the "total" field
    total_data['Total'] = get_cell_string(grand_total_count,grand_total_miles)

    # ok now make a data structure that has the rows and cols i want
    # then make it a dataframe
    data = []
    current_year = 0
    for row in result.itertuples():
        #print(row.Year, row.Month, row.miles, row.count)
        # row is a named tuple → very fast

        # new year? add a row to data
        if row.Year != current_year:
            # data for this row, and the data cell for this record
            _cell_data = get_cell_string(row.count, row.miles)

            # data for year total
            # tuple of result instead
            count_miles = tuple(result.loc[result['Year'] == row.Year, ['count', 'miles']].sum())
            _total_data = get_cell_string(count_miles[0], count_miles[1])

            element = {"Year": row.Year,
                       calendar.month_abbr[row.Month]: _cell_data,
                       "Total": _total_data}
            data.append(element)

            # set the current_year
            current_year = row.Year

        else:
            # add a column to data for this cell data
            _cell_data = get_cell_string(row.count, row.miles)
            data[-1][calendar.month_abbr[row.Month]] = _cell_data

    # add the totals row to the data
    data.append(total_data)

    # now convert data to a dataframe
    report_df = pd.DataFrame(data)
    desired_order = list(calendar.month_abbr)
    desired_order[0] = 'Year'
    desired_order.append('Total')
    report_df_sorted = report_df[desired_order]
    report_df_sorted = report_df_sorted.fillna('')        # Replaces NaN with empty string
    print(report_df_sorted)

    print(" ")


def year_week_report(df):
    '''
    year week report
    '''
    print("============================")
    print("Year Week Report (150 min)")
    # print (STANDARD_RPT_HEADING_WK)
    # this report only for current year only
    this_year = datetime.datetime.now().year
    #this_week = int(datetime.datetime.now().strftime("%W"))
    _rpt_weeks = None

    for _year in [this_year - 1, this_year]:

        # go back 54 weeks for prev year
        if _year != this_year:
            #_rpt_weeks = range(this_week, 54)
            _rpt_weeks = range(0, 54)
        if _year == this_year:
            _rpt_weeks = rpt_weeks

        # week data just for current year?
        print(" ")
        print(STANDARD_RPT_HEADING_WK)
        for _week in _rpt_weeks:
            standard_rpt(df, _year, week=_week)

        standard_rpt(df, _year)

    print(" ")

@measure_time
def year_to_date_report(df):
    '''
    year to date report
    '''
    # day_of_year = datetime.datetime.now().timetuple()[7]
    # ok have date_doy in the df now.
    # so may a new df for each including where doy <= actual doy
    print("============================")
    print("Year to Date Comparison")

    day_of_now = datetime.datetime.now()
    day_of_year = day_of_now.timetuple()[7]
    print(STANDARD_RPT_HEADING)
    for _year in RPT_YEARS:
        date_str = f"{str(_year):7s}"
        ytd_total_rpt(df, date_str, _year, day_of_year)
    print("end of Year to Date Comparison")
    print("============================")
    print("")


@measure_time
def weight_report(df, weights):
    '''
    report using df and weight array
    '''
    # customize heading
    print("============================")
    print("Weight Report")
    heading = "year mo      Min   Mean Median    Max"

    print(heading)
    for _year in RPT_YEARS:
        # month data just for current year
        if _year == RPT_YEARS[-1]:
            print(" ")
            print(heading)
            for _month in rpt_months:
                date_str = f"{_year} {_month:2d}"
                if not df.empty:
                    wt_rpt(df, date_str, _year, _month)

        date_str = f"{str(_year):7s}"
        wt_rpt(df, date_str, _year)

    # weights historically
    # sort first
    wt_keys = list(weights.keys())
    wt_keys.sort()
    weights_sorted = {i: weights[i] for i in wt_keys}

    print("")
    print("Weight By First, Last Date")
    for k in weights_sorted:
        print(f"{k:3.0f} {weights_sorted[k]}")
    print(" ")

@measure_time
def descr_report(df):
    '''
    description report
    '''
    # for formatting in output later
    max_len = df['Descr'].str.len().max()

    print("descr_report()")
    # don't want all RPT_YEARS, just within the YEARS_TO_REPORT
    for _year in RPT_YEARS[-YEARS_TO_REPORT:]:

        # get count and sum by descr for the year
        rpt_df = df[df['Year'] == _year]

        # remove zero values- for things like workouts
        rpt_dfn = rpt_df[rpt_df['Miles'] > 0]

        # get the count/sum for the rpt_df
        results = rpt_dfn.groupby('Descr').agg(
            mean_miles=('Miles', 'mean'),
            mean_elev=('Elev', 'mean'), #Elevi?
            total_miles=('Miles', 'sum'),
            total_count=('Miles', 'count'),
            ).round({'mean_miles': 1, 'total_miles': 1})

        # HEREHERE
        #print(results.info())
        results["mean_elev"] = (
            results["mean_elev"]
            .round()
            .astype("Int64")
            )
        #print(results.info())

        # sort
        results_sorted = results.sort_values('total_count', ascending=False)

        # formatting- get Descr the same width as a max_len
        results_sorted = results_sorted.reset_index()
        results_sorted['Descr'] = results_sorted['Descr'].fillna('').str.ljust(max_len)

        #print the results
        print()
        print(f"Year: {_year}")

        #print(results_sorted.to_string(na_rep=''))

        # replace <NA> cells with ''
        print(
            results_sorted
            .astype(object)
            .replace({pd.NA: ''})
            .to_string()
            )

    print(" ")

@measure_time
def interval_report(newdf):
    '''
    7/30/365 interval report
    '''
    # interval- 7, 30, 365
    print("Interval 7/30/365 reports")
    print(INTERVAL_RPT_HEADING)

    for _interval in [7, 30, 365]:
        # year doesn't matter here
        standard_rpt(newdf, None, interval=_interval)

    # number of expected workout days this month/year
    print("")
    for _entity in ['month', 'year']:
        num_days = get_num_workout_days(_entity)
        print("Expected Workout Days so far this "
              f"{_entity.title()}: {num_days[0]}")
        print("Expected Gym Days so far this "
              f"{_entity.title()}: {num_days[1]}")

    # maintenance report
    day_of_now = convert_date_to_unixdays(datetime.datetime.now())
    print("")

    maint_events = get_maint_event_data()

    print("Maintenance Report")
    for k, v in maint_events.items():
        # compute interval from maint event to now
        _interval = day_of_now - v
        print(f"Since Last {k}")
        standard_rpt(newdf, None, interval=_interval)
        print("")


def main():
    '''
    read raw data
    process it- compute new cols or set formats etc for existing data
    report on it as desired
    '''
    # csv file
    infilename = "workouts.csv"
    df = read_raw_data(infilename)

    # walk laps
    #unique_walk_descr = []

    # columns
    # making data frame
    # print ("Raw Data List(df)")
    # data_columns = list(df)
    # list(data_columns)

    # process dataframe
    weights = {}
    df = process_df(
        df,
        weights=weights
        )

    # needed
    #weights = processed_data['weights'] # do we need this?

    # at this point, the df object has all of the raw and computed data.
    # what remains is displaying it as desired

    # get the columns
    # print ("Computed Data List(df)")
    # data_columns = list(df)
    # print(df.info())
    # print(f"count {df['Date'].count()}")
    # print(f"min date {df['Date'].min()}")
    #col_info = pd.DataFrame({
    #    'column': df.columns,
    #    'dtype': df.dtypes.values
    #    })
    #print(col_info)


    # call report functions
    #reads suite file and executes code based upon what's in the suite file

    args = sys.argv[1:]
    if len(args) != 1:
        print("Specify the run suite file")
        sys.exit()

    # first, print out the last event for easier searching
    # for ease of searching in the output
    last_descr = df['Descr'][len(df.index)-1]
    print(f"Last Activity {last_descr}")

    # assign the filename
    infilename = args[0]
    # infilename = "test_suite.txt"
    # read the suite file
    with open(infilename, 'r', encoding='utf-8') as infile:
        lines = [line.rstrip() for line in infile]
    # loop the lines, execute the functions in the file
    for _l in lines:
        # check for # in 1st char
        if _l[0] == '#':
            continue

        # all take (df) except weight_report(df, weights)
        current_func = ''
        if _l.find('weight_report') == 0:
            current_func = f"{_l}(df, weights)"
        else:
            current_func = f"{_l}(df)"

        try:
            print(f"calling {current_func}")
            exec(current_func)
        # Exception
        except SyntaxError as exc:
            print(f"{exc} {current_func}")

    newdf = years_to_report_summary(df)
    interval_report(newdf)

    counter_report(timer_counter, "Timer Report")

if __name__ == '__main__':
    main()
