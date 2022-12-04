from typing import List

from django.http import HttpRequest

from app.models import Contact, Citizenship, Transport
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

    return {
        'phone_number_checkboxes': phone_number_checkboxes,
        'whatsapp_checkboxes': whatsapp_checkboxes,
        'citizenship_checkboxes': citizenship_checkboxes,
        'transport_checkboxes': transport_checkboxes,

        'citizenships': citizenships,
        'transports': transports,

        'executor_ids': executor_ids,
        'executors': executors,
        'count': count,
    }
