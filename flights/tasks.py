from celery import task, Task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.core.cache import cache
from .utils import get_destination_calls, get_cheapest_ticket_per_day, get_direction_keys, get_checked_flight, get_cheapest_ticket

import requests
import inspect
import collections
import sys
import json


@periodic_task(
    run_every=crontab(minute=0, hour=0),
    name="task_cache_cheapest_flights",
    ignore_result=True
)
def task_cache_cheapest_flights():
    urls = get_destination_calls()
    for destination, url in urls:
        data = json.loads(requests.get(url).content)['data']
        cheapest_tickets_per_day = get_cheapest_ticket_per_day(data)
        cache.set(destination, cheapest_tickets_per_day, 2 * 24 * 60 * 60)


@periodic_task(
    run_every=crontab(minute=0, hour='*/1'),
    name="task_validate_flights",
    ignore_result=True
)
def task_validate_flights():
    for direction in get_direction_keys():
        fly_from, fly_to = direction.split("-")
        
        flights = cache.get(direction)
        for date, ticket in flights.items():
            day = date.strftime("%d/%m/%Y")
            flight = get_checked_flight(ticket['booking_token'])

            if flight['flights_invalid']:
                flights[date] = get_cheapest_ticket(fly_from, fly_to, day)
                continue
            if flight['price_change']:
                flights[date]['price'] = flight["conversion"]["amount"]

        cache.set(direction, flights, 2 * 24 * 60 * 60)


# This allows retrieving corresponding function by a task name. 
# TaskInfo = collections.namedtuple("TaskInfo", "fullname name task")
# ALL_TASKS = {
#     __name__ + "." + _k: TaskInfo(__name__ + "." + _k, _k, _v)
#     for _k, _v in inspect.getmembers(sys.modules[__name__])
#     if isinstance(_v, Task)
# }
