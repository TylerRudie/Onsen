from datetime import timedelta, date
from collections import Counter
import atlas.models

def add_business_days(from_date, number_of_days):
    to_date = from_date
    while number_of_days:
       to_date += timedelta(1)
       if to_date.weekday() < 5: # i.e. is not saturday or sunday
           number_of_days -= 1
    return to_date


def sub_business_days(from_date, number_of_days):
    to_date = from_date
    while number_of_days:
       to_date += timedelta(-1)
       if to_date.weekday() < 5: # i.e. is not saturday or sunday
           number_of_days -= 1
    return to_date


def get_default_pool():
    try:
        return atlas.models.pool.objects.get(default=True)
    except atlas.models.pool.DoesNotExist:
        return None


def get_hw_staus_stats(hwType):

    c = Counter([item.status for item in atlas.models.hardware.objects.filter(type=hwType)])
    return c.items()