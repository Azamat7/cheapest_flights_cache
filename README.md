# Cached calendar of cheapest flights for TOP 10 directions

### Deployed: [cheapest-flights-cache.herokuapp.com](http://cheapest-flights-cache.herokuapp.com/)


### Run locally:

Celery beat for scheduling tasks
```
python manage.py celery beat --loglevel=info
```

Celery worker to execute tasks:
```
python manage.py celery worker --loglevel=info
```

Django server:
```
python manage.py runserver
```

### Implementation details:

#### task_cache_cheapest_flights
Celery task which runs everyday at midnight. Given 10 destinations, it finds the cheapest flight for every day and stores in the cache table.
#### task_validate_flights
This task runs every hour. Basically, it validates the cache entries. If the flight is invalid, it finds another cheapest flight. If the price has been changed, it updates the price of the given flight. This task runs under many assumptions, which may not be correct.

