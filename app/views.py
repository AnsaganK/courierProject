import csv
import json
from itertools import count

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.db.models import Q, F, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse

from app.forms import CityForm, UserCreateForm, ProfileForm, ProfileCreateForm, BicycleForm, UserUpdateForm, \
    CitizenshipForm, CitizenshipTypeForm, OFCForm, ArchiveFileForm, ArchiveFileUpdateForm, ExecutorForm
from app.models import Executor, City, OFC, Bicycle, Profile, Citizenship, CitizenshipType, ArchiveFile, ExecutorHours, \
    Day, DayHour, Contact, Period, Transport
from app.service.executor import get_query_parameters, get_active_executors
from app.service.file import get_file_data
from app.tasks import create_executors_for_file_task, create_cities_for_file_task, create_executor_hours_for_file_task, \
    create_executor_phones_for_file_task
from app.utils import check_role
from utils import show_form_errors, get_generated_password, get_paginator

CURATOR = Profile.RoleChoices.CURATOR
ADMIN = Profile.RoleChoices.ADMIN
SUPPORT = Profile.RoleChoices.SUPPORT
WEEK_DAYS = [
    'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
]


#
#                               Flat page views
#
@login_required
@check_role([ADMIN], redirect_url='/executor')
def home(request):
    city_count = City.objects.count()
    ofc_count = OFC.objects.count()

    curator_count = Profile.objects.filter(role=Profile.RoleChoices.CURATOR).count()
    curator_with_teams_count = User.objects.exclude(executors=None).count()

    executors = Executor.objects.all()
    active_executors = get_active_executors()
    bicycles = Bicycle.objects.all()
    bicycle_count = bicycles.count()
    bicycle_used_count = bicycles.exclude(executor=None).count()

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
        'bicycle_used_count': bicycle_used_count,
        'debtor_count': debtor_count,
    })


@login_required
@check_role([ADMIN, CURATOR])
def statistic(request):
    last_periods = Period.objects.all().order_by('-final_date')[:4]
    last_periods = last_periods[::-1]
    executors = get_active_executors()

    user = request.user
    profile = user.profile
    if profile.role == CURATOR:
        executors = executors.filter(curator=user)

    executors = executors.annotate(sum_hours=Sum(F('executor_hours__day_hours__hour'), default=0)).order_by(
        '-sum_hours')

    context = {
        'periods': last_periods,
    }
    context.update(get_query_parameters(request, executors, paginate=False))
    context.update({'week_days': WEEK_DAYS})
    return render(request, 'app/page/statistic.html', context)


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
            messages.success(request, f'Город "{city.name}" успешно добавлен')
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
            messages.success(request, f'Город "{city.name}" успешно изменен')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:city_list'))


@login_required
@check_role([ADMIN])
def city_delete(request, pk):
    city = get_object_or_404(City, pk=pk)
    name = city.name
    city.delete()
    messages.success(request, f'Город "{name}" успешно удален')
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
            messages.success(request, f'Файл "{file.filename}" сохранен')
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
    messages.success(request, f'Начата выгрузка городов из файла "{file.filename}" ')
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
            messages.success(request, f'ЦФЗ "{ofc.address}" создано')
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
            messages.success(request, f'ЦФЗ "{ofc.address}" изменено')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:ofc_list'))


@login_required
@check_role([ADMIN])
def ofc_delete(request, pk):
    ofc = get_object_or_404(OFC, pk=pk)
    address = ofc.address
    ofc.delete()
    messages.success(request, f'ЦФЗ "{address}" удалено')
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
                messages.success(request, f'{profile.get_role_display()} создан')
            else:
                show_form_errors(request, profile_form.errors)
        else:
            show_form_errors(request, user_form.errors)
    return redirect(reverse('app:curator_list'))


@login_required
@check_role([ADMIN])
def curator_list(request):
    curators = User.objects.filter(profile__role=Profile.RoleChoices.CURATOR)
    roles = Profile.RoleChoices.choices
    password = get_generated_password()
    return render(request, 'app/staff/curator/list.html', {
        'curators': curators,
        'password': password,
        'roles': roles
    })


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
            messages.success(request, f'Профиль пользователя "{user.username}" успешно изменен')
        else:
            messages.error(request, 'Ошибка при изменении')

    return redirect(reverse('app:curator_list'))


@login_required
@check_role([ADMIN])
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    username = user.username
    user.delete()
    messages.success(request, f'Пользователь "{username}" успешно удален')
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
@check_role([ADMIN, CURATOR])
def executor_list(request):
    user = request.user
    profile = user.profile
    if profile.role == ADMIN:
        executors = Executor.objects.all()
    else:
        executors = Executor.objects.filter(curator=request.user)

    executors = executors.annotate(sum_hours=Sum(F('executor_hours__day_hours__hour'), default=0)).order_by(
        '-sum_hours')

    context = {
        'executor_debtor_ids': Executor.objects.exclude(
            id__in=get_active_executors().values_list('id', flat=True)).exclude(bicycle=None).values_list('id',
                                                                                                          flat=True)
    }
    context.update(get_query_parameters(request, executors))
    context.update({'week_days': WEEK_DAYS})
    return render(request, 'app/executor/list.html', context)


@login_required
@check_role([CURATOR])
def executor_list_free(request):
    executors = Executor.objects.filter(curator=None)
    context = get_query_parameters(request, executors)
    return render(request, 'app/executor/free.html', context)


@login_required
@check_role([CURATOR])
def executor_add_for_curator(request, pk):
    executor = get_object_or_404(Executor, pk=pk)
    user = request.user
    if not executor.curator:
        executor.curator = user
        executor.save()
        messages.success(request, f'Исполнитель "{executor.get_full_name}" добавлен')
    else:
        messages.error(request, f'У данного исполнителя есть куратор: {executor.curator.get_full_name()}')
    return redirect(reverse('app:executor_list_free'))


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
        'contact_types': Contact.TypeChoices.choices
    })


@login_required()
def executor_detail_json(request, executor_id):
    executor = get_object_or_404(Executor, executor_id=executor_id)
    executor_hours = executor.executor_hours.all().order_by('period__final_date')

    executor_serialize = serialize('json', [executor, ]),
    executor_json = json.loads(executor_serialize[0])[0]["fields"]
    executor_json["transport"] = executor.transport.name if executor.transport else None
    executor_json["OFC"] = executor.OFC.address if executor.OFC else None
    executor_json["citizenship"] = executor.citizenship.name if executor.citizenship else None
    executor_json["citizenship_type"] = executor.citizenship_type.name if executor.citizenship_type else None
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
    print(executor_json)
    print(executor_hours_objects)
    return JsonResponse({
        'executor': executor_json,
        'executor_hours': executor_hours_objects,
        'week_days': WEEK_DAYS,
    })


def executor_hours_detail(request, executor_id):
    executor = get_object_or_404(Executor, executor_id=executor_id)
    executor_hours = executor.executor_hours.all().order_by('period__final_date')
    week_days = [
        'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
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
        'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
    ]
    filename = executor_id.replace('/', '-')
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response, delimiter=";")

    headline_row = ['ЦФЗ', 'Сотрудник', 'Период', 'Табельный номер'] + [week_day for week_day in week_days] + ['Итого']
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
            code = post['bicycle_code']

            bicycle = None
            if code and code[0]:
                bicycle = Bicycle.objects.get_or_create(code=code[0])
                if bicycle[1]:
                    bicycle[0].save()
                bicycle = bicycle[0]
                if bicycle.get_executor:
                    messages.warning(request, 'Этот велосипед уже занят')
                    bicycle = executor.bicycle

            executor = form.save(commit=False)
            executor.bicycle = bicycle
            executor.save()

            executor.contacts.all().delete()
            for c in contacts:
                contact = Contact.objects.create(executor=executor, identifier=c, type=contacts[c])
                contact.save()
            messages.success(request, f'Данные о "{executor.get_full_name}" изменены')
        else:
            show_form_errors(request, form.errors)
    return redirect(executor.get_absolute_url())


@login_required
def executor_delete(request, pk):
    executor = get_object_or_404(Executor, pk=pk)
    full_name = executor.get_full_name
    executor.delete()
    messages.success(request, f'Исполнитель "{full_name}" удален')
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
        executors = Executor.objects.filter(
            Q(last_name__icontains=query) | Q(first_name__icontains=query) | Q(
                patronymic__icontains=query) | Q(executor_id__icontains=query)).order_by('-pk').values(
            'executor_id', 'last_name', 'first_name', 'patronymic', 'id')[:5]
        return JsonResponse({
            'executors': list(executors)
        })
    return redirect(reverse('app:home'))


@login_required
def executor_salary_calculator(request):
    pass


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
            messages.success(request, f'Файл {file.filename} сохранен')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:executor_phones_file_list'))


def executor_phones_file_parse(request, pk):
    file = get_object_or_404(ArchiveFile, pk=pk)
    create_executor_phones_for_file_task.delay(pk)
    messages.success(request, f'Начата выгрузка телефонов исполнителей из файла "{file.filename}" ')
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
            messages.success(request, f'Файл "{file.filename}" сохранен')
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
    messages.success(request, f'Начата выгрузка часов исполнителей из файла "{file.filename}" ')
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
            messages.success(request, f'Файл "{file.filename}" сохранен')
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
    messages.success(request, f'Начата выгрузка исполнителей из файла "{file.filename}" ')
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
            messages.success(request, f'Велосипед "{bicycle.code}" создан')
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
def bicycle_detail(request, code):
    bicycle = get_object_or_404(Bicycle, code=code)
    return render(request, 'app/bicycle/detail.html', {
        'bicycle': bicycle
    })


@login_required
def bicycle_update(request, code):
    bicycle = get_object_or_404(Bicycle, code=code)
    if request.method == 'POST':
        form = BicycleForm(request.POST, instance=bicycle)
        if form.is_valid():
            form.save()
            messages.success(request, f'Велосипед "{bicycle.code}" изменен')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:bicycle_list'))


@login_required
def bicycle_delete(request, code):
    bicycle = get_object_or_404(Bicycle, code=code)
    code = bicycle.code
    bicycle.delete()
    messages.success(request, f'Велосипед "{code}" удален')
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
            messages.success(request, f'Гражданство "{citizenship.name}" создано')
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
            messages.success(request, f'Гражданство "{citizenship.name}" изменено')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:citizenship_list'))


@login_required
def citizenship_delete(request, pk):
    citizenship = get_object_or_404(Citizenship, pk=pk)
    name = citizenship.name
    citizenship.delete()
    messages.success(request, f'Гражданство "{name}" удалено')
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
            messages.success(request, f'Тип гражданства "{citizenship_type.name}" создан')
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
            messages.success(request, f'Тип гражданства "{citizenship_type.name}" изменен')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:citizenship_type_list'))


@login_required
def citizenship_type_delete(request, pk):
    citizenship_type = get_object_or_404(CitizenshipType, pk=pk)
    name = citizenship_type.name
    citizenship_type.delete()
    messages.success(request, f'Тип гражданства "{name}" удален')
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
            messages.success(request, f'Файл "{archive_file.filename}" создан')
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
            messages.success(request, f'Данные файла "{archive_file.filename}" изменен')
        else:
            show_form_errors(request, form.errors)
    return redirect(reverse('app:archive_file_list'))


@login_required
def archive_file_delete(request, pk):
    archive_file = get_object_or_404(ArchiveFile, pk=pk)
    pk = archive_file.pk
    archive_file.delete()
    messages.success(request, f'Архивный файл "{pk}" удален')
    return redirect(reverse('app:archive_file_list'))


def archive_file_get_status(request, pk):
    archive_file = get_object_or_404(ArchiveFile, pk=pk)
    return JsonResponse({
        'status': archive_file.status
    })


#
#                                   Error pages
#
def error_404_view(request, exception):
    return render(request, '404.html')


def error_403_view(request, exception):
    return render(request, '403.html')
