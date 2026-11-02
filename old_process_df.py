def process_df(df):
    '''
    go through raw data and set new rows
    also populate weights dict
    '''

    # weight checker
    weights = {}

    # loop through rows
    for index, row in df.iterrows():

        # assign None first to fix data incompatibilities
        df.loc[index, 'Date_year'] = None
        df.loc[index, 'Date_month'] = None
        df.loc[index, 'Date_dom'] = None
        df.loc[index, 'Date_doy'] = None

        # new fmt
        df.loc[index, 'Date_year'] = row["Year"]
        df.loc[index, 'Date_month'] = row["Month"]
        df.loc[index, 'Date_dom'] = row["Day"]

        # old df had DATE, which would actually be handy-- yyyy/mm/dd
        date_str = f'{row["Year"]:04}/{row["Month"]:02}/{row["Day"]:02}'
        df.loc[index, 'Date'] = str(date_str)

        # compute doy from python datetime obj
        df.loc[index, 'Date_doy'] = int(datetime.date(row["Year"],
                                        row["Month"],
                                        row["Day"]).timetuple()[7]
                                        )

        df.loc[index, 'Date_unixdays'] = convert_date_to_unixdays(
                                        datetime.datetime(row["Year"],
                                                          row["Month"],
                                                          row["Day"])
                                        )

        # add week of year
        df.loc[index, 'Date_week'] = convert_date_to_week(
                                        datetime.datetime(row["Year"],
                                                          row["Month"],
                                                          row["Day"])
                                        )

        # calories
        calories = row['Cal']
        if isinstance(calories, int):
            df.loc[index, 'Calories'] = calories
        elif isinstance(calories, float):
            if not math.isnan(calories):
                df.loc[index, 'Calories'] = int(calories)
            else:
                df.loc[index, 'Calories'] = pd.NA

        # VAM- make it an int
        vam = row['VAM']
        if isinstance(vam, float):
            if not math.isnan(vam):
                df.loc[index, 'VAMi'] = int(vam)
            else:
                df.loc[index, 'VAMi'] = pd.NA

        # format wt- could be blank, in which case it's a float nan
        # but we'd like it to be an int- pd.NA is a float so convert
        # to int but you can't do that
        # so even though wt is an int, make it a float in the df
        wt = df.loc[index, 'Wt']
        if isinstance(wt, str):
            wt = wt.strip()
            if len(wt) > 0:
                wt = float(wt)
                # df.loc[index, 'Wt'] = int(f"{wt}")
                df.loc[index, 'Wt'] = wt
            else:
                df.loc[index, 'Wt'] = pd.NA
        else:
            df.loc[index, 'Wt'] = pd.NA

        # weight checker
        # if this weight is in weights, update the date
        # if not, add it
        # print (type(wt))
        if isinstance(wt, float):
            if not math.isnan(wt):
                # old way
                #weights[wt] = date_str
                # new way
                # tuple- 0 is the first 1 is the most recent
                if wt in weights:
                    # update 2nd element
                    weights[wt] = (weights[wt][0],date_str)
                else:
                    # define tuple
                    weights[wt] = (date_str,0)

        # determine event
        # dtype=pd.StringDtype()

        # new fmt===============
        # compute Time Tot and asc/desc if blank
        # convert to min otherwise
        time_tot = df.loc[index, 'Time_Tot']
        asc_desc = pd.NA

        # compute Time Tot and asc/desc if blank
        if isinstance(time_tot, str):
            df.loc[index, 'Time_Tot_Min'] = convert_to_mins(
                df.loc[index, 'Time_Tot'])
        else:
            asc = convert_to_mins(df.loc[index, 'Time_Asc'])
            desc = convert_to_mins(df.loc[index, 'Time_Desc'])
            time_tot = asc + desc
            if desc > 0:
                asc_desc = round(asc/desc, 2)
            df.loc[index, 'Time_Tot_Min'] = time_tot
            df.loc[index, 'Time_Asc_Min'] = asc
            df.loc[index, 'Time_Desc_Min'] = desc
            df.loc[index, 'Asc_Desc'] = asc_desc

        # time stop, rest_60 calculation
        time_stop = df.loc[index, 'Time_Stop']
        # compute if it's a str, if empty it will be a float nan
        if isinstance(time_stop, str):

            time_stop_min = convert_to_mins(df.loc[index, 'Time_Stop'])
            df.loc[index, 'Time_Stop_Min'] = time_stop_min

            if df.loc[index, 'Time_Tot_Min'] > 0:
                rest_60 = (float)(60) * time_stop_min / \
                    df.loc[index, 'Time_Tot_Min']
                df.loc[index, 'Rest_60_Min'] = round(rest_60, 2)

                # want numbers like 3.80, not 3.8
                # use Decimal to fix the 100ths? does not work
                # don't want this to be a string
                # getcontext().prec = 3
                # rest_60 = Decimal(60 * time_stop_min) /
                # Decimal(df.loc[index, 'Time_Tot_Min'])
                # df.loc[index, 'Rest_60_Min'] = rest_60
                # will be a Decimal value, does pandas like it?

            else:
                # make a float nan
                # df.loc[index, 'Rest_60'] = time_stop
                df.loc[index, 'Rest_60_Min'] = pd.NA

        else:
            # this is also a float nan
            # df.loc[index, 'Rest_60'] = time_stop
            df.loc[index, 'Rest_60_Min'] = pd.NA

        # weather
        weather = df.loc[index, 'Weather']

        # recompute miles, sec_per_lap if laps
        # some walking isn't laps, just use raw app/gps miles for those
        laps = df.loc[index, 'Laps']

        if not math.isnan(laps):
            descr = str(df.loc[index, 'Descr']).lower()
            track_info = get_track_info(
                descr,
                df.loc[index, 'Time_Tot_Min'],
                laps
                )

            df.loc[index, 'Sec_per_lap'] = track_info['sec_per_lap']
            df.loc[index, 'Miles'] = track_info['track_miles']

        # need miles to calculate event type
        # miles might be in raw data or might be calculated if at track
        #if row["Miles"] != df.loc[index, 'Miles']:
        #    print(f"{date_str} {df.loc[index, 'Miles']} {row['Miles']}")

        #miles = df.loc[index, 'Miles']
        this_event = get_event(df.loc[index, 'Miles'])
        df.loc[index, 'Event'] = this_event

        # compute Elev- want to be an int
        elev = df.loc[index, 'Elev']
        if not math.isnan(elev):
            df.loc[index, 'Elevi'] = int(elev)
        else:
            df.loc[index, 'Elevi'] = pd.NA

        # compute mph
        mph = None
        if df.loc[index, 'Time_Tot_Min'] > 0:
            mph = (float)(60) * df.loc[index, 'Miles'] / \
                df.loc[index, 'Time_Tot_Min']
            df.loc[index, 'Mph'] = round(mph, 1)
            # float(f"{mph:.1f}")
        else:
            df.loc[index, 'Mph'] = pd.NA

        # walking-laps
        # if laps is not empty, add to a list
        # if not math.isnan(laps):
        #    descr = str(df.loc[index, 'Descr'])
        #    print (f"{descr} {laps}")
        #    if descr not in unique_walk_descr:
        #        unique_walk_descr.append(descr)

        # compute grade
        elev_feet = float((100 * df.loc[index, 'Elev']))
        half_trip_feet = float((df.loc[index, 'Miles']/2)*5280)
        grade = 0

        if half_trip_feet > 0:
            grade = elev_feet / half_trip_feet
        df.loc[index, 'Grade'] = round(grade, 1)

        # put the "new row" into a new frame?
        # or make new frames out of filtered requests

        # convert fitbit elements to ints
        # these are raw col names, append "i" for the int values
        fb_elements = [
            'FB_P',
            'FB_V',
            'FB_M',
            'FB_L',
            'FB_AVG',
            'FB_CL'
        ]
        for _e in fb_elements:
            _e_raw = df.loc[index, _e]
            _ei = _e + "i" # integer value name
            # convert float to int
            if isinstance(_e_raw, float):
                if not math.isnan(_e_raw):
                    df.loc[index, _ei] = int(_e_raw)
                else:
                    df.loc[index, _ei] = pd.NA
            else:
                df.loc[index, _ei] = pd.NA

    # prepare retval
    retval = {
        "df": df,
        "weights": weights
    }
    return retval

