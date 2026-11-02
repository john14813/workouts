import csv


#    raw_columns = [
#        "DATE", *************** 0
#        "TIME", *************** 1
#        "asc",  *************** 2
#        "desc", *************** 3
#        "asc/desc", # computed
#        "Stop Time", *************** 5
#        "LAPS",
#        "sec/lap, rest60", # computed
#        "miles",
#        "elev",
#        "grade", # computed
#        "cal",
#        "VAM",
#        "min/mile", # computed
#        "mph", # computed
#        "wt",
#        "descr"
#    ]

def time_convert(time_mins):
    '''
    time_mins is minutes.fractional_minutes, but it's a string
    return hh:mm:ss
    '''
    retval = ""
    if time_mins == "":
        return retval
    
    #print (f"{type(time_mins)}, {time_mins}")
    hrs = int(float(time_mins)/60)
    mins = int( float(time_mins) - hrs*60)
    secs = int( 60 * (float(time_mins) - int(float(time_mins))))

    #retval = f"{hrs}:{mins}:{secs}"
    retval = f"{hrs:02}:{mins:02}:{secs:02}"
    return retval


def main():
    # define input, output files
    in_filename = 'workouts.csv'
    out_filename = 'workouts_enh.csv'

    outlines = []

    # opening the CSV file
    with open(in_filename, mode ='r')as file:
    
        # reading the CSV file
        csvFile = csv.reader(file)
        
        # displaying the contents of the CSV file
        line_number = 0
        for lines in csvFile:
            #print(lines)
            line_number += 1

            if line_number == 1:
                # write the header columns
                # matches the data below
                # need quotes on each col?
                line_out = "Year,Month,Day,"
                line_out += "Time Tot,Time Asc,Time Desc,Time Stop,"
                line_out += "Laps,Weather,"
                line_out += "Miles,Elev,"
                line_out += "Cal,VAM,Wt,"
                line_out += "Descr"

                outlines.append(line_out)

                continue

            # convert columns of interest
            # 0 date 'Wed 09/10/97'
            new_date_list = lines[0].split(" ")[1].split('/')
            new_date_year = int(new_date_list[2])
            if new_date_year > 90:
                new_date_year += 1900
            else:
                new_date_year += 2000
            new_date_month = int(new_date_list[0])
            new_date_day = int(new_date_list[1])

            # times- 1,2,3,5. these come over as minutes.fractional_minutes
            # if 2,3 are populated, don't both with 1
            if lines[2] == '':
                pass
                # convert lines[1] time
                time_tot = time_convert(lines[1])
                time_asc = ''
                time_desc = ''
            else:
                pass
                # convert lines[2], lines[3] times
                time_tot = ''
                time_asc = time_convert(lines[2])
                time_desc = time_convert(lines[3])

            time_stop = time_convert(lines[5])

            # laps
            # only relevant for tracks
            # also used for weather on bike rides
            # do I care?

            # but i do care about that

            # if asc is populated, it's a ride
            # populate weather
            # otherwise, it's a walk
            # populate laps
            weather = ''
            laps = ''
            if lines[2] != '':
                # bike
                # this is weather
                weather = lines[6]
            else:
                # walk
                # laps
                laps = lines[6]

            # miles, elev
            miles = ''
            if lines[8] != '':
                miles = round(float(lines[8]),2)
            elev = lines[9]

            # cal, vam, wt
            cal = lines[11]
            vam = lines[12]
            wt = lines[15]

            # desc
            descr = lines[16]

            # build the output line
            data_out = []
            # write the output line
            #    raw_columns = [
            #        "DATE", *************** 0
            #        "TIME", *************** 1
            #        "asc",  *************** 2
            #        "desc", *************** 3
            #        "asc/desc", # computed
            #        "Stop Time", *************** 5
            #        "LAPS", 6
            #        "sec/lap, rest60", # computed 7
            #        "miles", 8
            #        "elev", 9
            #        "grade", # computed 10
            #        "cal", 11
            #        "VAM", 12
            #        "min/mile", # computed 13
            #        "mph", # computed 14
            #        "wt", 15
            #        "descr" 16
            #    ]
            # Date
            line_out = f"{new_date_year},{new_date_month},{new_date_day},"

            # tot, asc, desc time, stop time
            line_out += f"{time_tot},{time_asc},{time_desc},{time_stop},"

            # laps, weather
            line_out += f"{laps},{weather},"

            # miles, elev
            line_out += f"{miles},{elev},"

            # cal, vam, wt
            line_out += f"{cal},{vam},{wt},"

            # descr
            line_out += f"{descr}"

            outlines.append(line_out)

    # loop through line out ansd write to file
    for _outlines in outlines:
        print (f"{_outlines}")


main()
