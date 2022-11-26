from django.contrib.auth.models import User
from django import template

register = template.Library()


@register.filter(name='check_role')
def check_role(user: User, role: str) -> bool:
    if not user.is_authenticated:
        return False
    profile = user.profile
    if profile.role == role:
        return True
    return False
