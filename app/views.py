from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect, reverse

from app.forms import CityForm, UserCreateForm, ProfileForm, ProfileCreateForm, BicycleForm, UserUpdateForm, \
    CitizenshipForm, CitizenshipTypeForm, OFCForm, ArchiveFileForm, ArchiveFileUpdateForm
from app.models import Executor, City, OFC, Bicycle, Profile, Citizenship, CitizenshipType, ArchiveFile, ExecutorHours, \
    Day, DayHour
from app.service.file import get_file_data
from app.tasks import create_executors_for_file_task, create_cities_for_file_task, create_executor_hours_for_file_task
from utils import show_form_errors, get_generated_password, get_paginator


#
#                               Flat page views
#
@login_required
def home(request):
    city_count = City.objects.count()
    ofc_count = OFC.objects.count()

    curator_count = Profile.objects.filter(role=Profile.RoleChoices.CURATOR).count()
    curator_with_teams_count = User.objects.exclude(executors=None).count()

    executor_count = Executor.objects.count()

    bicycle_count = Bicycle.objects.count()
    bicycle_used_count = 0
    return render(request, 'app/page/home.html', {
        'city_count': city_count,
        'ofc_count': ofc_count,

        'curator_count': curator_count,
        'curator_with_teams_count': curator_with_teams_count,

        'executor_count': executor_count,

        'bicycle_count': bicycle_count
    })


#
#                               City views
#
@login_required
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
def city_list(request):
    cities = City.objects.all()
    return render(request, 'app/city/list.html', {
        'cities': cities
    })


@login_required
def city_detail(request, pk):
    city = get_object_or_404(City, pk=pk)
    return render(request, 'app/city/detail.html', {
        'city': city
    })


@login_required
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
def city_delete(request, pk):
    city = get_object_or_404(City, pk=pk)
    name = city.name
    city.delete()
    messages.success(request, f'Город "{name}" успешно удален')
    return redirect(reverse('app:city_list'))


@login_required
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
def city_file_list(request):
    files = ArchiveFile.objects.filter(type=ArchiveFile.TypeChoices.CITY)
    return render(request, 'app/city/file/list.html', {
        'files': files
    })


@login_required
def city_file_parse(request, pk):
    file = get_object_or_404(ArchiveFile, pk=pk)
    create_cities_for_file_task.delay(pk)
    messages.success(request, f'Начата выгрузка городов из файла "{file.filename}" ')
    return redirect(reverse('app:city_file_list'))


#
#                               OFC views
#
@login_required
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
def ofc_list(request):
    ofcs = OFC.objects.select_related('city').all()
    ofcs = get_paginator(request, ofcs, 25)
    cities = City.objects.all()
    return render(request, 'app/ofc/list.html', {
        'ofcs': ofcs,
        'cities': cities
    })


@login_required
def ofc_detail(request, pk):
    ofc = get_object_or_404(OFC, pk=pk)
    return render(request, 'app/ofc/detail.html', {
        'ofc': ofc
    })


@login_required
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
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'app/staff/curator/detail.html', {
        'user': user
    })


@login_required
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
def executor_create(request):
    if request.method == 'POST':
        pass
    genders = Executor.GenderChoices.choices
    citizenships = Citizenship.objects.all()
    citizenship_types = CitizenshipType.objects.all()
    ofcs = OFC.objects.all()
    roles = Executor.RoleChoices.choices
    curators = User.objects.filter(profile__role=Profile.RoleChoices.CURATOR)
    return render(request, 'app/executor/create.html', {
        'genders': genders,
        'citizenships': citizenships,
        'citizenship_types': citizenship_types,
        'ofcs': ofcs,
        'roles': roles,
        'curators': curators
    })


@login_required
def executor_list(request):
    executors = Executor.objects.all()
    count = executors.count()
    executors = get_paginator(request, executors, 50)
    return render(request, 'app/executor/list.html', {
        'executors': executors,
        'count': count
    })


@login_required
def executor_detail(request, executor_id):
    executor = get_object_or_404(Executor, executor_id=executor_id)
    executor_hours = executor.executor_hours.all()
    week_days = [
        'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
    ]
    return render(request, 'app/executor/detail.html', {
        'executor': executor,
        'executor_hours': executor_hours,
        'week_days': week_days
    })


def executor_hours_detail(request, executor_id):
    executor = get_object_or_404(Executor, executor_id=executor_id)
    executor_hours = executor.executor_hours.all()
    week_days = [
        'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
    ]
    return render(request, 'app/executor/hours/private.html', {
        'executor': executor,
        'executor_hours': executor_hours,
        'week_days': week_days
    })


@login_required
def executor_update(request, code):
    pass


@login_required
def executor_delete(request, pk):
    executor = get_object_or_404(Executor, pk=pk)
    full_name = executor.get_full_name
    executor.delete()
    messages.success(request, f'Исполнитель "{full_name}" удален')
    return redirect(reverse('app:executor_list'))


@login_required
def executor_salary_calculator(request):
    pass


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
    return render(request, 'app/executor/hours/file/list.html', {
        'files': files
    })


@login_required
def executor_hours_file_preview(request, pk):
    archive_file = get_object_or_404(ArchiveFile, pk=pk)
    executor_hours = archive_file.executor_hours.all().order_by('ofc__address')
    days = DayHour.objects.filter(executor_hour__in=archive_file.executor_hours.all()).order_by('day_id').distinct(
        'day').values('day__date')

    days_hour = DayHour.objects.filter(executor_hour__in=archive_file.executor_hours.all()).order_by('day_id').distinct(
        'day').values('day__date')
    return render(request, 'app/executor/hours/file/preview.html', {
        'archive_file': archive_file,
        'executor_hours': executor_hours,
        'days': days,
        'days_hour': days_hour
    })


@login_required
def executor_hours_file_parse(request, pk):
    file = get_object_or_404(ArchiveFile, pk=pk)
    create_executor_hours_for_file_task.delay(pk)
    messages.success(request, f'Начата выгрузка часов исполнителей из файла "{file.filename}" ')
    return redirect(reverse('app:executor_list'))


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
    return redirect(reverse('app:executor_list'))


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
    citizenships = Citizenship.objects.all()
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
