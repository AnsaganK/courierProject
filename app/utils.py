from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render

from app.models import Profile


def check_role(roles: list[Profile.RoleChoices]):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            user = request.user
            print(roles)
            print(user.profile.role)
            if user.profile.role in roles:
                return function(request, *args, **kwargs)
            return render(request, '403.html')

        return wrapper

    return decorator
