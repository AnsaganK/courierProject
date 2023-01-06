from django.contrib.auth.models import User
from django.db.models import Sum, F

from app.models import Profile, Executor
from app.service.executor import get_active_executors, get_query_parameters
from app.utils import WEEK_DAYS


def get_executors_context_for_user(request, user: User = None):
    if not user:
        user = request.user
        if not user.is_authenticated:
            return False
    profile = user.profile
    if profile.role in [Profile.RoleChoices.ADMIN, Profile.RoleChoices.ACCOUNTANT]:
        executors = Executor.objects.all()
    else:
        executors = Executor.objects.filter(curator=user)

    executors = executors.annotate(sum_hours=Sum(F('executor_hours__day_hours__hour'), default=0)).order_by(
        '-created_at')

    context = {
        'executor_debtor_ids': Executor.objects.exclude(
            id__in=get_active_executors().values_list('id', flat=True)).exclude(bicycle=None).values_list('id',
                                                                                                          flat=True)
    }
    context.update(get_query_parameters(request, executors))
    context.update({'week_days': WEEK_DAYS})
    return context
