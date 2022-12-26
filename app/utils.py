from typing import Optional

from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, reverse

from app.models import Profile

WEEK_DAYS = [
    'ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВСК'
]


def check_role(roles: list, redirect_url: Optional[str] = None):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user.profile.role in roles:
                return function(request, *args, **kwargs)
            if redirect_url:
                return redirect(redirect_url)
            return render(request, 'error/403.html')

        return wrapper

    return decorator
