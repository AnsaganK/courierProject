from django import template
from django.db.models import Sum

from app.models import Period, Executor, DayHour

register = template.Library()


@register.filter(name='get_hours_for_period')
def get_hours_for_period(executor, period_id):
    hours = DayHour.objects.filter(executor_hour__period_id=period_id, executor_hour__executor=executor).aggregate(
        Sum('hour')).get('hour__sum')
    return hours if hours else '-'
