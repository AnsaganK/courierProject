from django.db.models import QuerySet

from app.models import Period


def get_last_periods(limit: int = 4) -> QuerySet:
    last_periods = Period.objects.all().order_by('-final_date')[:limit]
    last_periods = last_periods[::-1]
    return last_periods
