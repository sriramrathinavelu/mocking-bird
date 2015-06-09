from datetime import datetime
from datetime import timedelta


def fututeTime(minutes):
    now = datetime.now()
    return now + timedelta(minutes=minutes)


def threeHoursFromNow():
    now = datetime.now()
    return now.replace(hour=now.hour+3)


def threeHoursFromTime(time):
    return time.replace(time=time.hour+3)


def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


def unix_time_millis(dt):
    return unix_time(dt) * 1000.0
