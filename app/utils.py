from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, reverse

from app.models import Profile


def check_role(roles: list[Profile.RoleChoices], redirect_url: str | None = None):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user.profile.role in roles:
                return function(request, *args, **kwargs)
            if redirect_url:
                return redirect(redirect_url)
            return render(request, '403.html')

        return wrapper

    return decorator
