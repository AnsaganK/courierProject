from typing import List

from django.http import HttpRequest

from app.models import Contact, Citizenship, Transport, Period, Executor
from utils import get_paginator


def get_query_parameters(request: HttpRequest, executors: list):
    data = dict(request.GET)
    phone_number_checkboxes = data.get('phone_number', [])
    if 'on' in phone_number_checkboxes:
        executors = executors.exclude(phone_number=None)
    elif 'off' in phone_number_checkboxes:
        executors = executors.filter(phone_number=None)

    whatsapp_checkboxes = data.get('whatsapp', [])
    if 'on' in whatsapp_checkboxes:
        executors = executors.filter(contacts__type=Contact.TypeChoices.WHATSAPP)
    elif 'off' in whatsapp_checkboxes:
        executors = executors.exclude(contacts__type=Contact.TypeChoices.WHATSAPP)

    citizenship_checkboxes = data.get('citizenship')
    if citizenship_checkboxes:
        executors = executors.filter(citizenship__in=citizenship_checkboxes)

    transport_checkboxes = data.get('transport')
    if transport_checkboxes:
        executors = executors.filter(transport__in=transport_checkboxes)
    count = executors.count()
    executor_ids = executors.values_list('id', flat=True)

    executors = get_paginator(request, executors, 50)
    citizenships = Citizenship.objects.all()
    transports = Transport.objects.all()
    active_executor_ids = get_active_executors().values_list('id', flat=True)
    return {
        'phone_number_checkboxes': phone_number_checkboxes,
        'whatsapp_checkboxes': whatsapp_checkboxes,
        'citizenship_checkboxes': citizenship_checkboxes,
        'transport_checkboxes': transport_checkboxes,

        'citizenships': citizenships,
        'transports': transports,
        'active_executor_ids': active_executor_ids,

        'executor_ids': executor_ids,
        'executors': executors,
        'count': count,
    }


def get_active_executors():
    last_periods = Period.objects.all().order_by('-final_date')[:4]
    last_periods = last_periods[::-1]
    executors = Executor.objects.filter(executor_hours__period__in=last_periods).distinct()
    return executors
