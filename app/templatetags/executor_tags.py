from django import template
from django.db.models import Sum, QuerySet
from django.urls import reverse

from app.models import Period, Executor, DayHour, ExecutorConfig

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


@register.filter(name='get_first_day_hour_for_internship')
def get_first_day_hour_for_internship(executor):
    config = ExecutorConfig.objects.order_by('-pk').first()
    internship_hours = config.internship_hours
    day_hour = DayHour.objects.filter(executor_hour__executor=executor, hour__gte=1).order_by(
        'day__date').first()
    if day_hour:
        return f'{day_hour.day.date} | {day_hour.hour}'
    else:
        return f'Меньше {internship_hours} часов'


@register.filter(name='get_first_day_hour_for_initial')
def get_first_day_hour_for_initial(executor):
    day_hour = DayHour.objects.filter(executor_hour__executor=executor, hour__gt=0).order_by('day__date').first()
    if day_hour:
        return f'{day_hour.day.date} | {day_hour.hour}'
    else:
        return f'Часов нет'
