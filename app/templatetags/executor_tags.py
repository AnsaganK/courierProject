from django import template
from django.db.models import Sum, QuerySet
from django.urls import reverse

from app.models import Period, Executor, DayHour

register = template.Library()


@register.filter(name='get_hours_for_period')
def get_hours_for_period(queryset, period_id):
    if type(queryset) == QuerySet:
        hours = DayHour.objects.filter(executor_hour__period_id=period_id,
                                       executor_hour__executor__in=queryset).aggregate(
            Sum('hour')).get('hour__sum')
    else:
        hours = DayHour.objects.filter(executor_hour__period_id=period_id,
                                       executor_hour__executor=queryset).aggregate(
            Sum('hour')).get('hour__sum')
    return hours if hours else '-'


@register.filter(name='get_whatsapp_url_for_executor')
def get_whatsapp_url_for_executor(executor, host):
    url = f'https://wa.me/{executor.get_whatsapp}?text=http://{host}' + reverse('app:executor_hours_detail',
                                                                         args=[executor.executor_id])
    return url
