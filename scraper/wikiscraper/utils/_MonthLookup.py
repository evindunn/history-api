import datetime as dt
import calendar
from calendar import Calendar


class MonthLookup:
    _INT_JAN = 1
    _INT_FEB = 2
    _INT_MAR = 3
    _INT_APR = 4
    _INT_MAY = 5
    _INT_JUN = 6
    _INT_JUL = 7
    _INT_AUG = 8
    _INT_SEP = 9
    _INT_OCT = 10
    _INT_NOV = 11
    _INT_DEC = 12

    _STR_JAN = "January"
    _STR_FEB = "February"
    _STR_MAR = "March"
    _STR_APR = "April"
    _STR_MAY = "May"
    _STR_JUN = "June"
    _STR_JUL = "July"
    _STR_AUG = "August"
    _STR_SEP = "September"
    _STR_OCT = "October"
    _STR_NOV = "November"
    _STR_DEC = "December"

    _INT_TO_STR = {
        _INT_JAN: _STR_JAN,
        _INT_FEB: _STR_FEB,
        _INT_MAR: _STR_MAR,
        _INT_APR: _STR_APR,
        _INT_MAY: _STR_MAY,
        _INT_JUN: _STR_JUN,
        _INT_JUL: _STR_JUL,
        _INT_AUG: _STR_AUG,
        _INT_SEP: _STR_SEP,
        _INT_OCT: _STR_OCT,
        _INT_NOV: _STR_NOV,
        _INT_DEC: _STR_DEC
    }

    _STR_TO_INT = {
        _STR_JAN: _INT_JAN,
        _STR_FEB: _INT_FEB,
        _STR_MAR: _INT_MAR,
        _STR_APR: _INT_APR,
        _STR_MAY: _INT_MAY,
        _STR_JUN: _INT_JUN,
        _STR_JUL: _INT_JUL,
        _STR_AUG: _INT_AUG,
        _STR_SEP: _INT_SEP,
        _STR_OCT: _INT_OCT,
        _STR_NOV: _INT_NOV,
        _STR_DEC: _INT_DEC
    }

    _CALENDAR = Calendar()
    _NOW = dt.datetime.now()

    @staticmethod
    def get_months(t):
        if t == str:
            return (
                MonthLookup._STR_JAN,
                MonthLookup._STR_FEB,
                MonthLookup._STR_MAR,
                MonthLookup._STR_APR,
                MonthLookup._STR_MAY,
                MonthLookup._STR_JUN,
                MonthLookup._STR_JUL,
                MonthLookup._STR_AUG,
                MonthLookup._STR_SEP,
                MonthLookup._STR_OCT,
                MonthLookup._STR_NOV,
                MonthLookup._STR_DEC
            )
        elif t == int:
            return (
                MonthLookup._INT_JAN,
                MonthLookup._INT_FEB,
                MonthLookup._INT_MAR,
                MonthLookup._INT_APR,
                MonthLookup._INT_MAY,
                MonthLookup._INT_JUN,
                MonthLookup._INT_JUL,
                MonthLookup._INT_AUG,
                MonthLookup._INT_SEP,
                MonthLookup._INT_OCT,
                MonthLookup._INT_NOV,
                MonthLookup._INT_DEC
            )
        else:
            return ()

    @staticmethod
    def get_days_for_month(month):
        if isinstance(month, str):
            month = MonthLookup._STR_TO_INT[month]
        _, days = calendar.monthrange(MonthLookup._NOW.year, month)
        return days

    @staticmethod
    def generate_days_in_year():
        dates = list()
        for month_idx in MonthLookup._INT_TO_STR.keys():
            days_in_month = MonthLookup.get_days_for_month(month_idx)
            for day in range(1, days_in_month + 1):
                dates.append(
                    "{}_{}".format(MonthLookup._INT_TO_STR[month_idx], day)
                )
        return dates

    def __getitem__(self, item):
        if isinstance(item, int):
            return MonthLookup._INT_TO_STR[item]
        elif isinstance(item, str):
            return MonthLookup._STR_TO_INT[item]
        else:
            raise KeyError
