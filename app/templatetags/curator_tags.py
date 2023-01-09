from datetime import datetime, timedelta

import pytz
from django import template
from django.db.models import Sum, QuerySet
from django.urls import reverse

from app.models import Period, Executor, DayHour, ExecutorConfig

register = template.Library()


@register.filter(name='get_internship_curator_executors')
def get_internship_curator_executors(user, request):
    today = datetime.now(tz=pytz.UTC)

    start_date = request.GET.get('start_date')
    start_date = start_date[0] if type(start_date) is list else today - timedelta(days=7)

    final_date = request.GET.get('final_date')
    final_date = final_date[0] if type(final_date) is list else today

    internship_executors_count = Executor.objects.filter(
        curator=user, internship_date__gte=start_date, internship_date__lte=final_date
    ).count()
    return internship_executors_count
