from celery import task, Task
import requests
import inspect
import collections
import sys
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from .utils import get_destination_calls, get_cheapest_ticket_per_day, get_direction_keys, get_check_fights_url, is_valid_ticket
import json
from django.core.cache import cache


@periodic_task(
    run_every=(crontab(minute=0, hour=0)),
    name="task_cache_cheapest_flights",
    ignore_result=True
)
def task_cache_cheapest_flights():
    urls = get_destination_calls()
    for destination_arrival, url in urls:
        r = requests.get(url)
        data = json.loads(r.content)['data']
        cheapest_tickets_per_day = get_cheapest_ticket_per_day(data)
        cache.set(destination_arrival, cheapest_tickets_per_day, 2 * 24 * 60 * 60)


@periodic_task(
    run_every=(crontab(minute=0, hour='*/1')),
    name="task_validate_flights",
    ignore_result=True
)
def task_validate_flights():
    keys = get_direction_keys()

    for direction in keys:
        flights = cache.get(direction)

        fly_from, fly_to = direction.split("-")

        for key, value in flights.items():
            day = key.strftime("%d/%m/%Y")
            booking_token = value['booking_token']

            flights_checked = False
            data = None
            while not flights_checked:
                url = get_check_fights_url(booking_token=booking_token)
                r = requests.get(url)
                data = json.loads(r.content)
                flights_checked = data['flights_checked']

            if data['flights_invalid']:
                url = get_url(fly_from, fly_to, day, day)
                r = requests.get(url)
                data = json.loads(r.content)
                tickets = []
                for d in data:
                    tickets.append({k:d[k] for k in ("dTime", "aTime", "price", "booking_token")})

                ticket = min(tickets, key=lambda x: x["price"])
                flights[key] = ticket
                continue
            
            if data['price_change']:
                new_price = data["conversion"]["amount"]
                flights[key]['price'] = new_price

        cache.set(direction, flights, 2 * 24 * 60 * 60)


# This allows retrieving corresponding function by a task name. 
# TaskInfo = collections.namedtuple("TaskInfo", "fullname name task")
# ALL_TASKS = {
#     __name__ + "." + _k: TaskInfo(__name__ + "." + _k, _k, _v)
#     for _k, _v in inspect.getmembers(sys.modules[__name__])
#     if isinstance(_v, Task)
# }
