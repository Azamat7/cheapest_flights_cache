from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum


class Direction(Enum):
    ALA_TSE = 'ALA-TSE'
    TSE_ALA = 'TSE-ALA'
    ALA_MOW = 'ALA-MOW'
    MOW_ALA = 'MOW-ALA'
    ALA_CIT = 'ALA-CIT'
    CIT_ALA = 'CIT-ALA'
    TSE_MOW = 'TSE-MOW'
    MOW_TSE = 'MOW-TSE'
    TSE_LED = 'TSE-LED'
    LED_TSE = 'LED-TSE'


class CodeToCity(Enum):
    ALA = 'Алматы'
    TSE = 'Астана'
    MOW = 'Москва'
    LED = 'Петербург'
    CIT = 'Шымкент'


def code_to_city(code):
    city_from, city_to = code.split("-")
    city_from = CodeToCity[city_from].value
    city_to = CodeToCity[city_to].value
    return f'{city_from} - {city_to}'


def get_url(fly_from, fly_to, date_from, date_to, partner="picky", curr="KZT"):
    base = "https://api.skypicker.com/flights"
    final_url = f'{base}?fly_from={fly_from}&fly_to={fly_to}&partner={partner}&date_from={date_from}&date_to={date_to}&curr={curr}'
    return final_url


def get_destination_calls():
    today = datetime.date(datetime.now())
    day_after_one_month = today + timedelta(days=30)

    urls = []
    for destination_arrival in Direction:
        fly_from, fly_to = destination_arrival.value.split("-")
        url = get_url(
            fly_from=fly_from,
            fly_to = fly_to,
            date_from = today.strftime("%d/%m/%Y"),
            date_to = day_after_one_month.strftime("%d/%m/%Y"),
        )
        urls.append((destination_arrival.value, url))
    return urls


def get_cheapest_ticket_per_day(data):
    data_by_day = defaultdict(list)

    for d in data:
        day = datetime.date(datetime.fromtimestamp(d["dTime"]))
        data_by_day[day].append({k:d[k] for k in ("dTime", "aTime", "price", "booking_token")})

    for key in data_by_day.keys():
        data_by_day[key] = min(data_by_day[key], key=lambda x: x["price"])
    
    return data_by_day