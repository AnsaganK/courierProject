from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpRequest

import string
import secrets


def set_status(obj, status):
    obj.status = status
    obj.save()


def show_form_errors(request: HttpRequest, errors):
    for error in errors:
        print(error)
        messages.error(request, f'{errors[error]}')


def get_generated_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    return password


def get_paginator(request, queryset, count=12):
    paginator = Paginator(queryset, count)
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    return queryset
