from typing import List

from django.contrib import messages
from django.db.models import Sum, F
from django.http import HttpRequest

from app.models import Contact, Citizenship, Transport, Period, Executor, City, ExecutorHours
from app.templatetags.executor_tags import get_hours_for_period
from utils import get_paginator


def get_query_parameters(request: HttpRequest, executors: list, paginate: bool = True, returned_json: bool = False):
    data = dict(request.GET)
    is_filter = 0
    for parameter in data:
        if parameter in ['phone_number', 'whatsapp', 'citizenship', 'city', 'transport']:
            is_filter += 1
            print(parameter)

        if parameter == 'sort_type' and data.get('sort_type')[0]:
            is_filter += 1

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

    city_checkboxes = data.get('city')
    if city_checkboxes:
        print(city_checkboxes)
        executors = executors.filter(OFC__city_id__in=city_checkboxes)

    transport_checkboxes = data.get('transport')
    if transport_checkboxes:
        executors = executors.filter(transport__in=transport_checkboxes)

    executors = executors.annotate(sum_hours=Sum(F('executor_hours__day_hours__hour')))
    min_hours_input = data.get('min_hours')
    min_hours = min_hours_input[0] if type(min_hours_input) is list else ""
    if min_hours:
        executors = executors.filter(sum_hours__gte=int(min_hours))

    max_hours_input = data.get('max_hours')
    max_hours = max_hours_input[0] if type(max_hours_input) is list else ""
    if max_hours:
        executors = executors.filter(sum_hours__lte=int(max_hours))

    sort_type = data.get('sort_type')
    sort_type = sort_type[0] if type(sort_type) is list else ""
    if sort_type == 'name_asc':
        executors = executors.order_by('last_name')
    if sort_type == 'name_desc':
        executors = executors.order_by('-last_name')
    if sort_type == 'hours_asc':
        executors = executors.order_by('sum_hours')
    if sort_type == 'hours_desc':
        executors = executors.order_by('-sum_hours')
    if sort_type == 'id_asc':
        executors = executors.order_by('executor_id')
    if sort_type == 'id_desc':
        executors = executors.order_by('-executor_id')

    executors = executors.select_related('curator')
    executors = executors.select_related('OFC')
    executors = executors.select_related('citizenship')

    if (min_hours and max_hours) and (int(min_hours) > int(max_hours)):
        messages.warning(request, 'Часы: наименьшее не может быть больше наибольшего')

    count = executors.count()
    executor_ids = executors.values_list('id', flat=True)
    last_periods = Period.objects.all().order_by('-final_date')[:4]
    last_periods = last_periods[::-1]
    if paginate:
        executors = get_paginator(request, executors, 40)
        if returned_json:
            executors_json = []
            for executor in executors:
                # print(executor)
                executor_json = {
                    'executor_id': executor.executor_id,
                    'citizenship': executor.citizenship.name if executor.citizenship else '-',
                    'full_name': executor.get_full_name,
                    'phone_number': executor.phone_number,
                    'OFC': executor.OFC.address if executor.OFC else '-',
                    'curator': executor.curator.profile.get_full_name if executor.curator else '-',
                    'get_whatsapp': executor.get_whatsapp,
                    'get_whatsapp_url': executor.get_whatsapp_url,
                    'get_absolute_url': executor.get_absolute_url(),
                    'get_api_url': executor.get_api_url(),
                    'hours': [{
                        'hour': get_hours_for_period(executor, last_period)
                    } for last_period in last_periods],
                    'hours_sum': executor.get_active_hours_sum,
                    'sort_type': sort_type
                }
                executors_json.append(executor_json)
            context = {
                'executors': executors_json,
                'next_page': executors.next_page_number() if executors.has_next() else 0,
                'has_next': executors.has_next(),
                'page': executors.number,
            }
            # print(context)
            return context
    citizenships = Citizenship.objects.all()
    cities = City.objects.all().order_by('name')
    transports = Transport.objects.all()
    active_executor_ids = get_active_executors().values_list('id', flat=True)

    return {
        'phone_number_checkboxes': phone_number_checkboxes,
        'whatsapp_checkboxes': whatsapp_checkboxes,
        'citizenship_checkboxes': citizenship_checkboxes,
        'transport_checkboxes': transport_checkboxes,
        'sort_type': sort_type,

        'min_hours': min_hours,
        'max_hours': max_hours,

        'citizenships': citizenships,
        'cities': cities,
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


def add_ofc_for_executor(executor: Executor = None, many: bool = True):
    if many:
        executors = Executor.objects.filter(OFC=None, executor_hours=None)
        for executor in executors:
            last_executor_hours = executor.executor_hours.order_by('period__final_date').last()
            if last_executor_hours:
                ofc = last_executor_hours.ofc
                executor.OFC = ofc
                executor.save()
    else:
        last_executor_hours = executor.executor_hours.order_by('period__final_date').last()
        if last_executor_hours:
            ofc = last_executor_hours.ofc
            executor.OFC = ofc
            executor.save()
