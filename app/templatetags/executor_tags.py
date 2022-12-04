from django import template
from django.db.models import Sum, QuerySet

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
