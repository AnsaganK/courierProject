import csv
import datetime
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.db.models import Q, F, Sum, Value
from django.db.models.functions import Concat
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse

from app.forms import CityForm, UserCreateForm, ProfileForm, ProfileCreateForm, BicycleForm, UserUpdateForm, \
    CitizenshipForm, CitizenshipTypeForm, OFCForm, ArchiveFileForm, ArchiveFileUpdateForm, ExecutorForm, \
    ExecutorConfigForm, CuratorUpdateForm, CuratorProfileUpdateForm, CuratorPaymentForm
from app.models import Executor, City, OFC, Bicycle, Profile, Citizenship, CitizenshipType, ArchiveFile, DayHour, \
    Contact, Period, Transport, ExecutorConfig, PaymentForCurators
from app.service.executor import get_query_parameters, get_active_executors, get_internship_executors_by_date
from app.service.export import generate_file_for_executors
from app.service.period import get_last_periods
from app.service.staff import get_executors_context_for_user
from app.tasks import create_executors_for_file_task, create_cities_for_file_task, create_executor_hours_for_file_task, \
    create_executor_phones_for_file_task, create_executor_internship_date_for_file_task
from app.utils import check_role, WEEK_DAYS
from constants import HOST
from utils import show_form_errors, get_generated_password, get_paginator

CURATOR = Profile.RoleChoices.CURATOR
ADMIN = Profile.RoleChoices.ADMIN
SUPPORT = Profile.RoleChoices.SUPPORT
ACCOUNTANT = Profile.RoleChoices.ACCOUNTANT


#
#                               Flat page views
#
@login_required
@check_role([ADMIN, ACCOUNTANT], redirect_url='/executor')
def home(request):
    city_count = City.objects.count()
    ofc_count = OFC.objects.count()

    curator_count = Profile.objects.filter(role=Profile.RoleChoices.CURATOR).count()
    curator_with_teams_count = User.objects.exclude(executors=None).count()

    executors = Executor.objects.all()
    active_executors = get_active_executors()
    bicycles = Bicycle.objects.all()
    bicycle_count = bicycles.count()

    active_executor_ids = get_active_executors().values_list('id', flat=True)
    debtor_count = Executor.objects.exclude(id__in=active_executor_ids).exclude(bicycle=None).count()
    return render(request, 'app/page/home.html', {
        'city_count': city_count,
        'ofc_count': ofc_count,
        'curator_count': curator_count,
        'curator_with_teams_count': curator_with_teams_count,
        'executor_count': executors.count(),
        'executor_active_count': active_executors.count(),
        'bicycle_count': bicycle_count,
        'bicycle_used_count': bicycle_count,
        'debtor_count': debtor_count,
    })


@login_required
@check_role([ADMIN, ACCOUNTANT, CURATOR])
def statistic(request):
    executors = get_active_executors()

    if request.user.profile.role == CURATOR:
        executors = executors.filter(curator=request.user)
    if request.GET.get('export') == 'true':
        file = generate_file_for_executors(request, executors)
        return file
    user = request.user
    profile = user.profile
    if profile.role == CURATOR:
        executors = executors.filter(curator=user)

    executors = executors.annotate(sum_hours=Sum(F('executor_hours__day_hours__hour'), default=0)).order_by(
        'sum_hours')

    context = {'periods': get_last_periods(), 'week_days': WEEK_DAYS}
    context.update(get_query_parameters(request, executors, paginate=True))
    return render(request, 'app/page/statistic.html', context)


@login_required
def profile(request):
    user = request.user
    role = user.profile.role
    if role == ADMIN:
        return render(request, 'app/staff/admin/profile.html', {
            'user': user
        })
    elif role == CURATOR:
        return render(request, 'app/staff/curator/detail.html', {
            'curator': user
        })
    elif role == SUPPORT:
        return render(request, 'app/staff/support/profile.html', {
            'user': user
        })
    return redirect(reverse('app:home'))


@login_required
@check_role([ADMIN, ACCOUNTANT, CURATOR])
def statistic_api(request):
    executors = get_active_executors()

    username = request.GET.get('curator')
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    profile = user.profile
    if profile.role == CURATOR:
        executors = executors.filter(curator=user)

    executors = executors.annotate(sum_hours=Sum(F('executor_hours__day_hours__hour'), default=0)).order_by(
        'sum_hours')

    executors = get_query_parameters(request, executors, paginate=True, returned_json=True)
    return JsonResponse(
        executors
    )


@login_required
@check_role([ADMIN])
def configuration(request):
    executor_config = ExecutorConfig.objects.first()
    if request.method == 'POST':
        form = ExecutorConfigForm(request.POST, instance=executor_config)
        if form.is_valid():
            form.save()
            messages.success(request, '???????????????????????? ?????????????? ????????????????')
        else:
            show_form_errors(request, form.errors)
        return redirect(reverse('app:configuration'))
    if not executor_config:
        executor_config = ExecutorConfig.objects.create()
        executor_config.save()

    return render(request, 'app/page/configuration.html', {
        'executor_config': executor_config
    })


#
#                               City views
#
@login_required
@check_role([ADMIN])
def city_create(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.save()
            messages.success(request, f'?????????? "{city.name}" ?????????????? ????????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:city_list'))


@login_required
@check_role([ADMIN])
def city_list(request):
    cities = City.objects.all()
    return render(request, 'app/city/list.html', {
        'cities': cities
    })


@login_required
@check_role([ADMIN])
def city_detail(request, pk):
    city = get_object_or_404(City, pk=pk)
    return render(request, 'app/city/detail.html', {
        'city': city
    })


@login_required
@check_role([ADMIN])
def city_update(request, pk):
    city = get_object_or_404(City, pk=pk)
    if request.method == 'POST':
        form = CityForm(request.POST, instance=city)
        if form.is_valid():
            form.save()
            messages.success(request, f'?????????? "{city.name}" ?????????????? ??????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:city_list'))


@login_required
@check_role([ADMIN])
def city_delete(request, pk):
    city = get_object_or_404(City, pk=pk)
    name = city.name
    city.delete()
    messages.success(request, f'?????????? "{name}" ?????????????? ????????????')
    return redirect(reverse('app:city_list'))


@login_required
@check_role([ADMIN])
def city_file_create(request):
    if request.method == 'POST':
        form = ArchiveFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.type = ArchiveFile.TypeChoices.CITY
            file.save()
            messages.success(request, f'???????? "{file.filename}" ????????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:city_file_list'))


@login_required
@check_role([ADMIN])
def city_file_list(request):
    files = ArchiveFile.objects.filter(type=ArchiveFile.TypeChoices.CITY)
    return render(request, 'app/city/file/list.html', {
        'files': files
    })


@login_required
@check_role([ADMIN])
def city_file_parse(request, pk):
    file = get_object_or_404(ArchiveFile, pk=pk)
    create_cities_for_file_task.delay(pk)
    messages.success(request, f'???????????? ???????????????? ?????????????? ???? ?????????? "{file.filename}" ')
    return redirect(reverse('app:city_file_list'))


#
#                               OFC views
#
@login_required
@check_role([ADMIN])
def ofc_create(request):
    if request.method == 'POST':
        form = OFCForm(request.POST)
        if form.is_valid():
            ofc = form.save()
            messages.success(request, f'?????? "{ofc.address}" ??????????????')
        else:
            show_form_errors(request, form.errors)
        return redirect(reverse('app:ofc_list'))
    return redirect(reverse('app:ofc_list'))


@login_required
@check_role([ADMIN])
def ofc_list(request):
    ofcs = OFC.objects.select_related('city').all()
    ofcs = get_paginator(request, ofcs, 25)
    cities = City.objects.all()
    return render(request, 'app/ofc/list.html', {
        'ofcs': ofcs,
        'cities': cities
    })


@login_required
@check_role([ADMIN])
def ofc_detail(request, pk):
    ofc = get_object_or_404(OFC, pk=pk)
    return render(request, 'app/ofc/detail.html', {
        'ofc': ofc
    })


@login_required
@check_role([ADMIN])
def ofc_update(request, pk):
    ofc = get_object_or_404(OFC, pk=pk)
    if request.method == 'POST':
        form = OFCForm(request.POST, instance=ofc)
        if form.is_valid():
            form.save()
            messages.success(request, f'?????? "{ofc.address}" ????????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:ofc_list'))


@login_required
@check_role([ADMIN])
def ofc_delete(request, pk):
    ofc = get_object_or_404(OFC, pk=pk)
    address = ofc.address
    ofc.delete()
    messages.success(request, f'?????? "{address}" ??????????????')
    return redirect(reverse('app:ofc_list'))


#
#                               Staff views
#
@login_required
@check_role([ADMIN])
def user_create(request):
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            profile_form = ProfileCreateForm(request.POST, instance=user.profile)
            if profile_form.is_valid():
                profile = profile_form.save()
                messages.success(request, f'{profile.get_role_display()} ????????????')
                return redirect(user.profile.get_redirect_url_by_role())
            else:
                show_form_errors(request, profile_form.errors)
        else:
            show_form_errors(request, user_form.errors)
    return redirect('app:home')


@login_required
@check_role([ADMIN, ACCOUNTANT])
def curator_list(request):
    curators = User.objects.filter(profile__role=Profile.RoleChoices.CURATOR).order_by('-pk')
    roles = Profile.RoleChoices.choices
    password = get_generated_password()

    start_date = request.GET.get('start_date') if request.GET.get('start_date') else (
            datetime.datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    final_date = request.GET.get('final_date') if request.GET.get('final_date') else datetime.datetime.today().strftime(
        '%Y-%m-%d')

    return render(request, 'app/staff/curator/list.html', {
        'curators': curators,
        'password': password,
        'roles': roles,
        'start_date': start_date,
        'final_date': final_date,
        'role': Profile.RoleChoices.CURATOR
    })


@login_required
@check_role([ADMIN])
def curator_detail(request, username):
    user = get_object_or_404(User, username=username)
    context = {'user': user}
    context.update({'curator': user, 'is_curator_preview': True})
    return render(request, 'app/staff/curator/profile.html', context)


@login_required()
@check_role([ADMIN, CURATOR])
def curator_update(request, username):
    curator = get_object_or_404(User, username=username)
    if request.method == 'POST':
        user_form = CuratorUpdateForm(request.POST, instance=curator)
        if user_form.is_valid():
            user = user_form.save()

            profile_form = CuratorProfileUpdateForm(request.POST, instance=user.profile)
            if profile_form.is_valid():
                profile = profile_form.save()
                messages.success(request, f'???????????? "{profile.get_full_name}" ????????????????')
            else:
                show_form_errors(request, profile_form.errors)

            payment_form = CuratorPaymentForm(request.POST, instance=user.payment_info)
            if payment_form.is_valid():
                payment_form.save()
            else:
                show_form_errors(request, profile_form.errors)

        else:
            show_form_errors(request, user_form.errors)
    if request.user == curator:
        return redirect(reverse('app:profile'))
    return redirect(reverse('app:curator_detail', args=[username]))


@login_required
@check_role([ADMIN, ACCOUNTANT])
def curator_preview_statistic(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile

    executors = get_active_executors().filter(curator=user)
    if request.GET.get('export') == 'true':
        file = generate_file_for_executors(request, executors)
        return file
    if profile.role == CURATOR:
        executors = executors.filter(curator=user)

    executors = executors.annotate(sum_hours=Sum(F('executor_hours__day_hours__hour'), default=0)).order_by(
        'sum_hours')

    context = {'periods': get_last_periods(), 'week_days': WEEK_DAYS}
    context.update(get_query_parameters(request, executors, paginate=True))
    context.update({'curator': user, 'is_curator_preview': True})
    return render(request, 'app/page/statistic.html', context)


@login_required
@check_role([ADMIN, ACCOUNTANT])
def curator_preview_internship_executor_list(request, username):
    user = get_object_or_404(User, username=username)
    internship_executors = get_internship_executors_by_date(user, request).values(
        'last_name', 'first_name', 'patronymic', 'executor_id', 'id', 'internship_date'
    )
    return JsonResponse({
        'executors': list(internship_executors),
        'count': internship_executors.count()
    }, status=200)


@login_required
@check_role([ADMIN, ACCOUNTANT])
def curator_preview_executor_list(request, username):
    user = get_object_or_404(User, username=username)
    context = get_executors_context_for_user(request, user)
    context.update({'curator': user, 'is_curator_preview': True})
    return render(request, 'app/executor/list.html', context)


@login_required
@check_role([ADMIN, ACCOUNTANT])
def curator_preview_executor_free_list(request, username):
    user = get_object_or_404(User, username=username)
    executors = get_active_executors().filter(curator=None).order_by('-created_at')
    context = get_query_parameters(request, executors)
    context.update({'week_days': WEEK_DAYS})
    context.update({'curator': user, 'is_curator_preview': True})
    return render(request, 'app/executor/free.html', context)


@login_required
@check_role([ADMIN, ACCOUNTANT, CURATOR])
def curator_preview_payments(request, username):
    user = get_object_or_404(User, username=username)
    periods = Period.objects.all().order_by('final_date')
    payments = PaymentForCurators.objects.filter(user=user).values_list('period_id', flat=True)
    paid_payments = payments.filter(is_paid=True)
    context = {
        'curator': user,
        'periods': periods,
        # 'curator_payments': payments,
        'paid_payments': paid_payments
    }
    context.update({'curator': user, 'is_curator_preview': True})
    return render(request, 'app/staff/curator/payment/list.html', context)


# Refactor
@login_required
@check_role([ADMIN, ACCOUNTANT, CURATOR])
def curator_preview_payment_detail(request, username, period_id):
    period = get_object_or_404(Period, id=period_id)
    user = get_object_or_404(User, username=username)

    last_period = Period.objects.filter(final_date__lte=period.final_date).order_by('-start_date').last()
    curator_payment = PaymentForCurators.objects.filter(period_id=period_id, user__username=username).first()
    config = ExecutorConfig.objects.first()
    current_day_hours = DayHour.objects.filter(executor_hour__period=period)
    previous_day_hours = DayHour.objects.filter(executor_hour__period__final_date__lt=period.final_date)

    internship_executors = Executor.objects.filter(
        curator=user,
        executor_hours__day_hours__in=current_day_hours
    ).exclude(
        executor_hours__day_hours__in=previous_day_hours
    ).distinct().order_by(
        'last_name'
    )

    executor_less_hours = Executor.objects.filter(
        curator=user,
        executor_hours__period__final_date__lt=period.final_date
    ).annotate(
        last_period_hours_sum=Sum('executor_hours__day_hours__hour', default=0)
    ).filter(
        last_period_hours_sum__lt=config.initial_hours
    )

    initial_executors = Executor.objects.filter(
        executor_hours__period__final_date__lte=period.final_date,
        executor_hours__day_hours__in=current_day_hours
    ).filter(
        (Q(id__in=executor_less_hours))
        |
        (Q(curator=user) &
         ~Q(executor_hours__day_hours__in=previous_day_hours))
    ).annotate(
        current_period_hours_sum=Sum('executor_hours__day_hours__hour')
    ).filter(
        current_period_hours_sum__gte=config.initial_hours
    ).distinct().order_by(
        'last_name'
    )

    internship_payment = user.payment_info.payment_for_internship_hours
    initial_payment = user.payment_info.payment_for_initial_hours

    context = {
        'period': period,
        'internship_executors': internship_executors,
        'initial_executors': initial_executors,
        'config': config,

        'internship_payment': internship_payment,
        'initial_payment': initial_payment,
        'internship_payment_sum': internship_payment * internship_executors.count(),
        'initial_payment_sum': initial_payment * initial_executors.count(),

        'week_days': WEEK_DAYS

    }
    context.update({'curator': user, 'is_curator_preview': True})
    return render(request, 'app/staff/curator/payment/detail.html', context)


@login_required
@check_role([CURATOR])
def curator_payments(request):
    username = request.user.username
    return curator_preview_payments(request, username)


@login_required
@check_role([CURATOR])
def curator_payment_detail(request, period_id):
    username = request.user.username
    return curator_preview_payment_detail(request, username, period_id)


@login_required
@check_role([ADMIN])
def support_list(request):
    supports = User.objects.filter(profile__role=Profile.RoleChoices.SUPPORT)
    roles = Profile.RoleChoices.choices
    password = get_generated_password()
    return render(request, 'app/staff/support/list.html', {
        'supports': supports,
        'password': password,
        'roles': roles
    })


@login_required
@check_role([ADMIN])
def accountant_list(request):
    accountants = User.objects.filter(profile__role=Profile.RoleChoices.ACCOUNTANT)
    roles = Profile.RoleChoices.choices
    password = get_generated_password()
    return render(request, 'app/staff/accountant/list.html', {
        'accountants': accountants,
        'password': password,
        'roles': roles
    })


@login_required
@check_role([ADMIN])
def admin_list(request):
    admins = User.objects.filter(profile__role=Profile.RoleChoices.ADMIN)
    roles = Profile.RoleChoices.choices
    password = get_generated_password()
    return render(request, 'app/staff/admin/list.html', {
        'admins': admins,
        'password': password,
        'roles': roles
    })


@login_required
@check_role([ADMIN])
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'app/staff/curator/detail.html', {
        'user': user
    })


@login_required
@check_role([ADMIN])
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        password = request.POST['password']
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.password1 = password
            profile.save()
            messages.success(request, f'?????????????? ???????????????????????? "{user.username}" ?????????????? ??????????????')
        else:
            messages.error(request, '???????????? ?????? ??????????????????')

    return redirect(reverse('app:curator_list'))


@login_required
@check_role([ADMIN])
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    username = user.username
    user.delete()
    messages.success(request, f'???????????????????????? "{username}" ?????????????? ????????????')
    return redirect(reverse('app:curator_list'))


#
#                               Executor views
#
@login_required
@check_role([ADMIN])
def executor_create(request):
    if request.method == 'POST':
        pass
    genders = Executor.GenderChoices.choices
    citizenships = Citizenship.objects.all()
    citizenship_types = CitizenshipType.objects.all()
    ofcs = OFC.objects.all()
    curators = User.objects.filter(profile__role=Profile.RoleChoices.CURATOR)
    return render(request, 'app/executor/create.html', {
        'genders': genders,
        'citizenships': citizenships,
        'citizenship_types': citizenship_types,
        'ofcs': ofcs,
        'curators': curators
    })


@login_required
@check_role([ADMIN, ACCOUNTANT, CURATOR])
def executor_list(request):
    user = request.user
    context = get_executors_context_for_user(request, user)
    return render(request, 'app/executor/list.html', context)


@login_required
@check_role([CURATOR])
def executor_list_free(request):
    executors = get_active_executors().filter(curator=None).order_by('-created_at')
    context = get_query_parameters(request, executors)
    context.update({'week_days': WEEK_DAYS})
    return render(request, 'app/executor/free.html', context)


@login_required
@check_role([ADMIN])
def executor_add_for_curator_by_admin(request, username, pk):
    user = get_object_or_404(User, username=username)
    executor = get_object_or_404(Executor, pk=pk)
    if not executor.curator:
        executor.curator = user
        executor.save()
        messages.success(request, f'?????????????????????? "{executor.get_full_name}" ????????????????')
    else:
        messages.error(request, f'?? ?????????????? ?????????????????????? ???????? ??????????????: {executor.curator.get_full_name()}')

    next = request.GET.get('next')
    if next:
        next_url = f'http://{HOST}{request.build_absolute_uri().split("?next=")[1]}'
        return redirect(next_url)

    return redirect(reverse('app:curator_preview_executor_free_list', args=[username]))


@login_required
@check_role([CURATOR])
def executor_add_for_curator(request, pk):
    executor = get_object_or_404(Executor, pk=pk)
    user = request.user
    if not executor.curator:
        executor.curator = user
        executor.save()
        messages.success(request, f'?????????????????????? "{executor.get_full_name}" ????????????????')
    else:
        messages.error(request, f'?? ?????????????? ?????????????????????? ???????? ??????????????: {executor.curator.get_full_name()}')

    next = request.GET.get('next')
    if next:
        next_url = f'http://{HOST}{request.build_absolute_uri().split("?next=")[1]}'
        return redirect(next_url)

    return redirect(reverse('app:executor_list_free'))


@login_required
@check_role([CURATOR])
def executor_add_for_curator_by_api(request, pk):
    executor = get_object_or_404(Executor, pk=pk)
    user = request.user
    if not executor.curator:
        executor.curator = user
        executor.save()
        return JsonResponse({
            'message': '?????????????????????? ????????????????'
        }, status=200)
    return JsonResponse({
        'message': f'?? ?????????????? ?????????????????????? ???????? ??????????????: {executor.curator.get_full_name()}',
    }, status=403)


@login_required
@check_role([ADMIN, CURATOR])
def executor_list_my(request):
    executors = Executor.objects.filter(curator=request.user)

    context = get_query_parameters(request, executors)

    return render(request, 'app/executor/list.html', context)


@login_required
@check_role([ADMIN, CURATOR, SUPPORT])
def executor_list_debtor(request):
    active_executor_ids = get_active_executors().values_list('pk', flat=True)
    executors = Executor.objects.exclude(bicycle=None).exclude(id__in=active_executor_ids)
    executors = get_paginator(request, executors, 50)
    return render(request, 'app/executor/debtor/list.html', {
        'executors': executors
    })


@login_required
def executor_detail(request, executor_id):
    executor = get_object_or_404(Executor, executor_id=executor_id)
    executor_hours = executor.executor_hours.all().order_by('period__final_date')

    return render(request, 'app/executor/detail.html', {
        'executor': executor,
        'executor_hours': executor_hours,
        'week_days': WEEK_DAYS,
        'genders': Executor.GenderChoices.choices,
        'citizenships': Citizenship.objects.all(),
        'citizenship_types': CitizenshipType.objects.all(),
        'curators': User.objects.filter(profile__role=Profile.RoleChoices.CURATOR),
        'ofcs': OFC.objects.all(),
        'transports': Transport.objects.all(),
        'bicycles': Bicycle.objects.all(),
        'contact_types': Contact.TypeChoices.choices,

        'host': HOST
    })


@login_required()
def executor_detail_api(request, executor_id):
    executor = get_object_or_404(Executor, executor_id=executor_id)
    executor_hours = executor.executor_hours.all().order_by('period__final_date')

    executor_serialize = serialize('json', [executor, ]),
    executor_json = json.loads(executor_serialize[0])[0]["fields"]
    executor_json["curator"] = executor.curator.profile.get_full_name if executor.curator else None
    executor_json["transport"] = executor.transport.name if executor.transport else None
    executor_json["OFC"] = executor.OFC.address if executor.OFC else None
    executor_json["citizenship"] = executor.citizenship.name if executor.citizenship else None
    executor_json["citizenship_type"] = executor.citizenship_type.name if executor.citizenship_type else None
    executor_json["bicycle"] = executor.bicycle.name if executor.bicycle else None
    executor_json["gender"] = executor.get_gender_display() if executor.gender else None
    executor_json["contacts"] = list(
        executor.contacts.all().values_list('type', 'identifier')) if executor.contacts.exists() else None

    executor_hours_objects = []
    for executor_hour in executor_hours:
        day_hours = []
        executor_day_hours = executor_hour.day_hours.all()
        for index, week_day in enumerate(WEEK_DAYS):
            try:
                day_hour = executor_day_hours[index]
                hour = day_hour.hour
            except:
                hour = '-'
            day_hours.append({
                'hour': hour
            })
        day_hours.append({"hour": executor_hour.get_hours_sum})
        executor_hours_objects.append({
            'executor': executor_hour.executor.get_full_name,
            'ofc': executor_hour.ofc.address,
            'transport': executor_hour.transport.name,
            'period': executor_hour.period.__str__(),
            'executor_id': executor_hour.executor.executor_id,
            'day_hours': day_hours
        })
    return JsonResponse({
        'executor': executor_json,
        'executor_hours': executor_hours_objects,
        'week_days': WEEK_DAYS,
    })


def executor_hours_detail(request, executor_id):
    executor = get_object_or_404(Executor, executor_id=executor_id)
    executor_hours = executor.executor_hours.all().order_by('period__final_date')
    week_days = [
        '??????????????????????', '??????????????', '??????????', '??????????????', '??????????????', '??????????????', '??????????????????????'
    ]
    return render(request, 'app/executor/hours/private.html', {
        'executor': executor,
        'executor_hours': executor_hours,
        'week_days': week_days
    })


def executor_hours_export(request, executor_id):
    executor = get_object_or_404(Executor, executor_id=executor_id)
    executor_hours = executor.executor_hours.all().order_by('period__final_date')
    week_days = [
        '??????????????????????', '??????????????', '??????????', '??????????????', '??????????????', '??????????????', '??????????????????????'
    ]
    filename = executor_id.replace('/', '-')
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response, delimiter=";")

    headline_row = ['??????', '??????????????????', '????????????', '?????????????????? ??????????'] + [week_day for week_day in week_days] + ['??????????']
    writer.writerow(headline_row)
    for executor_hour in executor_hours:
        executor_hour_row = [executor_hour.ofc, executor_hour.executor.get_full_name, executor_hour.period,
                             executor_hour.executor.executor_id] + \
                            [day_hour.hour if day_hour.hour else '' for day_hour in executor_hour.day_hours.all()] + [
                                executor_hour.get_hours_sum]
        writer.writerow(executor_hour_row)

    return response


@login_required
def executor_update(request, executor_id):
    executor = get_object_or_404(Executor, executor_id=executor_id)
    if request.method == 'POST':
        post = dict(request.POST)
        if post.get('identifier'):
            contacts = dict(zip(post['identifier'], post['type']))
        else:
            contacts = []
        form = ExecutorForm(request.POST, instance=executor)
        if form.is_valid():
            # code = post['bicycle_code']
            #
            # bicycle = None
            # if code and code[0]:
            #     bicycle = Bicycle.objects.get_or_create(code=code[0])
            #     if bicycle[1]:
            #         bicycle[0].save()
            #     bicycle = bicycle[0]
            #     if bicycle.get_executor:
            #         messages.warning(request, '???????? ?????????????????? ?????? ??????????')
            #         bicycle = executor.bicycle
            #
            # executor = form.save(commit=False)
            # executor.bicycle = bicycle
            executor.save()

            executor.contacts.all().delete()
            for c in contacts:
                contact = Contact.objects.create(executor=executor, identifier=c, type=contacts[c])
                contact.save()
            messages.success(request, f'???????????? ?? "{executor.get_full_name}" ????????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(executor.get_absolute_url())


@login_required
def executor_delete(request, pk):
    executor = get_object_or_404(Executor, pk=pk)
    full_name = executor.get_full_name
    executor.delete()
    messages.success(request, f'?????????????????????? "{full_name}" ????????????')
    return redirect(reverse('app:executor_list'))


@login_required
def executor_search(request):
    if request.method == 'POST':
        post = dict(request.POST)
        executor_id = post['query'][0]
        executor = get_object_or_404(Executor, executor_id=executor_id)
        return redirect(executor.get_absolute_url())
    elif request.method == 'GET':
        get = dict(request.GET)
        query = get['query'][0]
        executors = Executor.objects.annotate(
            fullname=Concat(F('last_name'), Value(' '), F('first_name'), Value(' '), F('patronymic'))
        ).filter(
            Q(fullname__icontains=query) | Q(executor_id__icontains=query)
        ).order_by('-pk').values(
            'executor_id', 'last_name', 'first_name', 'patronymic', 'id', 'curator', 'birth_date', 'phone_number'
        )[:5]
        return JsonResponse({
            'executors': list(executors)
        })
    return redirect(reverse('app:home'))


@login_required
def executor_salary_calculator(request):
    pass


#
#                                   Executor Internships (Samokat) Files
#
def executor_internships_file_list(request):
    files = ArchiveFile.objects.filter(type=ArchiveFile.TypeChoices.INTERNSHIP_SAMOKAT)
    files = get_paginator(request, files, 20)
    return render(request, 'app/executor/internship/samokat/list.html', {
        'files': files
    })


def executor_internships_file_create(request):
    if request.method == 'POST':
        form = ArchiveFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            file.type = ArchiveFile.TypeChoices.INTERNSHIP_SAMOKAT
            file.save()
            messages.success(request, f'???????? {file.filename} ????????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:executor_internships_file_list'))


def executor_internships_file_parse(request, pk):
    file = get_object_or_404(ArchiveFile, pk=pk)
    create_executor_internship_date_for_file_task.delay(pk)
    messages.success(request, f'???????????? ???????????????? ???????????????????? ???????????????????????? ???? ?????????? "{file.filename}" ')
    return redirect(reverse('app:executor_internships_file_list'))


#
#                                   Executor Phone Files
#
def executor_phones_file_list(request):
    files = ArchiveFile.objects.filter(type=ArchiveFile.TypeChoices.PHONE)
    files = get_paginator(request, files, 20)
    return render(request, 'app/executor/phone/file/list.html', {
        'files': files
    })


def executor_phones_file_create(request):
    if request.method == 'POST':
        form = ArchiveFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            file.type = ArchiveFile.TypeChoices.PHONE
            file.save()
            messages.success(request, f'???????? {file.filename} ????????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:executor_phones_file_list'))


def executor_phones_file_parse(request, pk):
    file = get_object_or_404(ArchiveFile, pk=pk)
    create_executor_phones_for_file_task.delay(pk)
    messages.success(request, f'???????????? ???????????????? ?????????????????? ???????????????????????? ???? ?????????? "{file.filename}" ')
    return redirect(reverse('app:executor_phones_file_list'))


#
#                                   Executor Hours Files
#
@login_required
def executor_hours_file_create(request):
    if request.method == 'POST':
        form = ArchiveFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.type = ArchiveFile.TypeChoices.HOURS
            file.save()
            messages.success(request, f'???????? "{file.filename}" ????????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:executor_hours_file_list'))


@login_required
def executor_hours_file_list(request):
    files = ArchiveFile.objects.filter(type=ArchiveFile.TypeChoices.HOURS)
    files = get_paginator(request, files, 20)
    return render(request, 'app/executor/hours/file/list.html', {
        'files': files
    })


@login_required
def executor_hours_file_preview(request, pk):
    archive_file = get_object_or_404(ArchiveFile, pk=pk)
    executor_hours = archive_file.executor_hours.all().order_by('ofc__address')
    day_hours = DayHour.objects.filter(executor_hour__in=archive_file.executor_hours.all()).order_by('day_id').distinct(
        'day')
    return render(request, 'app/executor/hours/file/preview.html', {
        'archive_file': archive_file,
        'executor_hours': executor_hours,
        'day_hours': day_hours,
    })


@login_required
def executor_hours_file_parse(request, pk):
    file = get_object_or_404(ArchiveFile, pk=pk)
    create_executor_hours_for_file_task.delay(pk)
    messages.success(request, f'???????????? ???????????????? ?????????? ???????????????????????? ???? ?????????? "{file.filename}" ')
    return redirect(reverse('app:executor_hours_file_list'))


@login_required
def executor_hours_file_delete(request, pk):
    file = get_object_or_404(ArchiveFile, pk=pk)
    filename = file.filename
    executor_hours = file.executor_hours.all()
    periods = Period.objects.filter(executor_hours__in=executor_hours)
    periods_list = [period.__str__() for period in periods.distinct()]
    periods = Period.objects.filter(id__in=set(periods.values_list('pk', flat=True)))
    print(executor_hours.delete())
    print(periods.delete())
    print(file.delete())

    messages.success(request, f'???????????? "{filename}" ???? ???????????? {periods_list} ??????????????')
    return redirect(reverse('app:executor_hours_file_list'))


#
#                                   Executor File views
#
@login_required
def executor_file_create(request):
    if request.method == 'POST':
        form = ArchiveFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.type = ArchiveFile.TypeChoices.EXECUTOR
            file.save()
            messages.success(request, f'???????? "{file.filename}" ????????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:executor_file_list'))


@login_required
def executor_file_list(request):
    files = ArchiveFile.objects.filter(type=ArchiveFile.TypeChoices.EXECUTOR)
    return render(request, 'app/executor/file/list.html', {
        'files': files
    })


@login_required
def executor_file_parse(request, pk):
    file = get_object_or_404(ArchiveFile, pk=pk)
    create_executors_for_file_task.delay(pk)
    messages.success(request, f'???????????? ???????????????? ???????????????????????? ???? ?????????? "{file.filename}" ')
    return redirect(reverse('app:executor_file_list'))


#
#                                   Bicycle views
#
@login_required
def bicycle_create(request):
    if request.method == 'POST':
        form = BicycleForm(request.POST)
        if form.is_valid():
            bicycle = form.save()
            messages.success(request, f'?????????????????? "{bicycle.name}" ????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:bicycle_list'))


@login_required
def bicycle_list(request):
    bicycles = Bicycle.objects.all()
    bicycles = get_paginator(request, bicycles, count=25)
    return render(request, 'app/bicycle/list.html', {
        'bicycles': bicycles
    })


@login_required
def bicycle_detail(request, pk):
    bicycle = get_object_or_404(Bicycle, pk=pk)
    return render(request, 'app/bicycle/detail.html', {
        'bicycle': bicycle
    })


@login_required
def bicycle_update(request, pk):
    bicycle = get_object_or_404(Bicycle, pk=pk)
    if request.method == 'POST':
        form = BicycleForm(request.POST, instance=bicycle)
        if form.is_valid():
            form.save()
            messages.success(request, f'?????????????????? "{bicycle.name}" ??????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:bicycle_list'))


@login_required
def bicycle_delete(request, pk):
    bicycle = get_object_or_404(Bicycle, pk=pk)
    name = bicycle.name
    bicycle.delete()
    messages.success(request, f'?????????????????? "{name}" ????????????')
    return redirect(reverse('app:bicycle_list'))


#
#                   Transport views
#

def transport_list(request):
    transports = Transport.objects.all()
    return render(request, 'app/transport/list.html', {
        'transports': transports
    })


#
#                                   Citizenship views
#
@login_required
def citizenship_create(request):
    if request.method == 'POST':
        form = CitizenshipForm(request.POST)
        if form.is_valid():
            citizenship = form.save()
            messages.success(request, f'?????????????????????? "{citizenship.name}" ??????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:citizenship_list'))


@login_required
def citizenship_list(request):
    citizenships = Citizenship.objects.all().order_by('name')
    return render(request, 'app/citizenship/list.html', {
        'citizenships': citizenships
    })


@login_required
def citizenship_detail(request, pk):
    citizenship = get_object_or_404(Citizenship, pk=pk)
    return render(request, 'app/citizenship/detail.html', {
        'citizenship': citizenship
    })


@login_required
def citizenship_update(request, pk):
    citizenship = get_object_or_404(Citizenship, pk=pk)
    if request.method == 'POST':
        form = CitizenshipForm(request.POST, instance=citizenship)
        if form.is_valid():
            form.save()
            messages.success(request, f'?????????????????????? "{citizenship.name}" ????????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:citizenship_list'))


@login_required
def citizenship_delete(request, pk):
    citizenship = get_object_or_404(Citizenship, pk=pk)
    name = citizenship.name
    citizenship.delete()
    messages.success(request, f'?????????????????????? "{name}" ??????????????')
    return redirect(reverse('app:citizenship_list'))


#
#                                   Citizenship type views
#
@login_required
def citizenship_type_create(request):
    if request.method == 'POST':
        form = CitizenshipTypeForm(request.POST)
        if form.is_valid():
            citizenship_type = form.save()
            messages.success(request, f'?????? ?????????????????????? "{citizenship_type.name}" ????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:citizenship_type_list'))


@login_required
def citizenship_type_list(request):
    citizenship_types = CitizenshipType.objects.all()
    return render(request, 'app/citizenship_type/list.html', {
        'citizenship_types': citizenship_types
    })


@login_required
def citizenship_type_detail(request, pk):
    citizenship_type = get_object_or_404(CitizenshipType, pk=pk)
    return render(request, 'app/citizenship_type/detail.html', {
        'citizenship_type': citizenship_type
    })


@login_required
def citizenship_type_update(request, pk):
    citizenship_type = get_object_or_404(CitizenshipType, pk=pk)
    if request.method == 'POST':
        form = CitizenshipTypeForm(request.POST, instance=citizenship_type)
        if form.is_valid():
            form.save()
            messages.success(request, f'?????? ?????????????????????? "{citizenship_type.name}" ??????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:citizenship_type_list'))


@login_required
def citizenship_type_delete(request, pk):
    citizenship_type = get_object_or_404(CitizenshipType, pk=pk)
    name = citizenship_type.name
    citizenship_type.delete()
    messages.success(request, f'?????? ?????????????????????? "{name}" ????????????')
    return redirect(reverse('app:citizenship_type_list'))


#
#                                   ArchiveFile views
#
@login_required
def archive_file_create(request):
    if request.method == 'POST':
        form = ArchiveFileForm(request.POST, request.FILES)
        if form.is_valid():
            archive_file = form.save()
            messages.success(request, f'???????? "{archive_file.filename}" ????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:archive_file_list'))


@login_required
def archive_file_list(request):
    archive_files = ArchiveFile.objects.all()
    types = ArchiveFile.TypeChoices.choices
    return render(request, 'app/archive_file/list.html', {
        'archive_files': archive_files,
        'types': types
    })


@login_required
def archive_file_detail(request, pk):
    archive_file = get_object_or_404(ArchiveFile, pk=pk)
    return render(request, 'app/archive_file/detail.html', {
        'archive_file': archive_file
    })


@login_required
def archive_file_update(request, pk):
    archive_file = get_object_or_404(ArchiveFile, pk=pk)
    if request.method == 'POST':
        form = ArchiveFileUpdateForm(request.POST, instance=archive_file)
        if form.is_valid():
            form.save()
            messages.success(request, f'???????????? ?????????? "{archive_file.filename}" ??????????????')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:archive_file_list'))


@login_required
def archive_file_delete(request, pk):
    archive_file = get_object_or_404(ArchiveFile, pk=pk)
    pk = archive_file.pk
    archive_file.delete()
    messages.success(request, f'???????????????? ???????? "{pk}" ????????????')
    return redirect(reverse('app:archive_file_list'))


def archive_file_get_status(request, pk):
    archive_file = get_object_or_404(ArchiveFile, pk=pk)
    return JsonResponse({
        'status': archive_file.status
    })


#
#                                   Error pages
#

def csrf_failure(request, reason=""):
    return render(request, 'error/403_csrf.html')


def error_500_view(request, *args, **kwargs):
    return render(request, 'error/500.html')


def error_404_view(request, exception):
    return render(request, 'error/404.html')


def error_403_view(request, exception):
    return render(request, 'error/403.html')
