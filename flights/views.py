from __future__ import absolute_import

from django.shortcuts import render, redirect
from django.core.cache import cache
from datetime import datetime
from . import utils

import celery


def home(request):
    destinations = []
    for direction in utils.get_direction_keys():
        cities = utils.code_to_city(direction)
        destinations.append([direction, cities])

    return render(request, "home.html", {"destinations": destinations})


def destination(request, code):
    
    flights = cache.get(code)

    cards = []

    for key, value in flights.items():
        day = key.strftime("%d-%b-%Y")
        departure = datetime.fromtimestamp(value['dTime']).strftime('%H:%M')
        arrival = datetime.fromtimestamp(value['aTime']).strftime('%H:%M')
        price = value['price']
        cards.append([day, departure, arrival, price])

    cards.sort(key = lambda x: datetime.strptime(x[0], "%d-%b-%Y"))
    cities = utils.code_to_city(code)
    return render(request, "destination.html", {"cards": cards, "code": code, "cities": cities})
