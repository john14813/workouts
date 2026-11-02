import datetime
from datetime import date, timedelta


def get_num_workout_days():
    '''
    take a datetime "now" object and return the number of workout days for this month
    loop through the days of the month up to now
    if it's a su mo we fri sat, add 1
    '''
    retval = 0
    delta_1 = timedelta(days=1)
    x_now = datetime.datetime.now()
    # 1st day of this month
    x_1st = datetime.datetime(x_now.year, x_now.month, 1)
    x_start = x_1st
    #print (f"{x_now} {x_1st}")

    while x_start <= x_now:
        # get day of the week of x_start
        dow = x_start.weekday()
        # Return the day of the week as an integer, where Monday is 0 and Sunday is 6. For example, date(2002, 12, 4).weekday() == 2, a Wednesday. See also isoweekday().
        #print (f"{dow}")

        if dow in [0,2,4,5,6]:
            retval += 1

        # increment
        x_start += delta_1

    return retval


def main():
    '''
    take a datetime "now" object and return the number of workout days for this month
    loop through the days of the month up to now
    if it's a su mo we fri sat, add 1
    '''

    num_days = get_num_workout_days()
    print (num_days)


if __name__ == '__main__':
    main()
