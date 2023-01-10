from datetime import datetime, timedelta

import pytz
from django import template
from django.db.models import Sum, QuerySet
from django.urls import reverse

from app.models import Period, Executor, DayHour, ExecutorConfig
from app.service.executor import get_internship_executors_by_date

register = template.Library()


@register.filter(name='get_internship_curator_executors')
def get_internship_curator_executors(user, request):
    internship_executors = get_internship_executors_by_date(user, request)
    return internship_executors.count()
