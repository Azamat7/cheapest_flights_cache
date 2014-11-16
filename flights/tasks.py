from celery import task, Task
import requests
import inspect
import collections
import sys
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from .utils import get_destination_calls, get_cheapest_ticket_per_day
import json
from django.core.cache import cache

# minute=0, hour=0
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


# This allows retrieving corresponding function by a task name. 
TaskInfo = collections.namedtuple("TaskInfo", "fullname name task")
ALL_TASKS = {
    __name__ + "." + _k: TaskInfo(__name__ + "." + _k, _k, _v)
    for _k, _v in inspect.getmembers(sys.modules[__name__])
    if isinstance(_v, Task)
}
