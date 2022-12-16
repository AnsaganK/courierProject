from typing import List

from django.contrib import messages
from django.db.models import Sum, F
from django.http import HttpRequest

from app.models import Contact, Citizenship, Transport, Period, Executor
from utils import get_paginator


def get_query_parameters(request: HttpRequest, executors: list, paginate: bool = True):
    data = dict(request.GET)
    is_filter = 0
    for parameter in data:
        if parameter in ['phone_number', 'whatsapp', 'citizenship', 'transport']:
            is_filter += 1
            print(parameter)

        if parameter == 'min_hours' and data.get('min_hours')[0]:
            is_filter += 1
        if parameter == 'max_hours' and data.get('max_hours')[0]:
            print(parameter, data.get('max_hours'))
            is_filter += 1

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

    min_hours_input = data.get('min_hours')
    min_hours = min_hours_input[0] if type(min_hours_input) is list else ""
    if min_hours:
        executors = executors.annotate(sum_hours=Sum(F('executor_hours__day_hours__hour')))
        executors = executors.filter(sum_hours__gte=int(min_hours))

    max_hours_input = data.get('max_hours')
    max_hours = max_hours_input[0] if type(max_hours_input) is list else ""
    if max_hours:
        executors = executors.annotate(sum_hours=Sum(F('executor_hours__day_hours__hour')))
        executors = executors.filter(sum_hours__lte=int(max_hours))

    executors = executors.select_related('curator')
    executors = executors.select_related('OFC')
    executors = executors.select_related('citizenship')

    if (min_hours and max_hours) and (int(min_hours) > int(max_hours)):
        messages.warning(request, 'Часы: наименьшее не может быть больше наибольшего')

    count = executors.count()
    executor_ids = executors.values_list('id', flat=True)

    if paginate:
        executors = get_paginator(request, executors, 50)
    citizenships = Citizenship.objects.all()
    transports = Transport.objects.all()
    active_executor_ids = get_active_executors().values_list('id', flat=True)

    return {
        'phone_number_checkboxes': phone_number_checkboxes,
        'whatsapp_checkboxes': whatsapp_checkboxes,
        'citizenship_checkboxes': citizenship_checkboxes,
        'transport_checkboxes': transport_checkboxes,

        'min_hours': min_hours,
        'max_hours': max_hours,

        'citizenships': citizenships,
        'transports': transports,
        'active_executor_ids': active_executor_ids,

        'executor_ids': executor_ids,
        'executors': executors,
        'count': count,
        'paginate': paginate,
        'is_filter': is_filter
    }


def get_active_executors():
    last_periods = Period.objects.all().order_by('-final_date')[:4]
    last_periods = last_periods[::-1]
    executors = Executor.objects.filter(executor_hours__period__in=last_periods).distinct()
    return executors
