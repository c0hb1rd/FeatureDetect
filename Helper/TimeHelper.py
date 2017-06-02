import time
from math import modf


class TimeHelper:
    def __init__(self):
        pass

    @staticmethod
    def getTime():
        date = time.localtime()
        return {
            # 'ms': milSecond,
            # 'year': date.tm_year,
            # 'mon': date.tm_mon,
            # 'day': date.tm_mday,
            'hour': date.tm_hour,
            'min': date.tm_min,
            'sec': date.tm_sec
        }

    @staticmethod
    def parseTime(date):
        t = time.strptime(date, "%Y-%m-%d")
        return time.mktime(t) * 1000

    @staticmethod
    def getStamp():
        return int(time.time() * 1000)

    @staticmethod
    def formatTime(timeStamp):
        fTime = modf(int(timeStamp) / 1000.0)
        date = time.localtime(fTime[1])

        year = str(date.tm_year)
        mon = date.tm_mon >= 10 and str(date.tm_mon) or "0" + str(date.tm_mon)
        day = date.tm_mday >= 10 and str(date.tm_mday) or "0" + str(date.tm_mday)
        hour = date.tm_hour >= 10 and str(date.tm_hour) or "0" + str(date.tm_hour)
        minutes = date.tm_min >= 10 and str(date.tm_min) or "0" + str(date.tm_min)
        sec = date.tm_sec >= 10 and str(date.tm_sec) or "0" + str(date.tm_sec)

        return "%s-%s-%s %s:%s:%s" % (year, mon, day, hour, minutes, sec)
