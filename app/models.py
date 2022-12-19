import os
import socket
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.shortcuts import reverse


class StatusChoices(models.TextChoices):
    WAIT = 'WAIT', 'Ожидание'
    WARNING = 'WARNING', 'Ожидание'
    SUCCESS = 'SUCCESS', 'Успешно'
    ERROR = 'ERROR', 'Ошибка'
    NOT_STARTED = 'NOT_STARTED', 'Не начато'


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class City(BaseModel):
    name = models.CharField(max_length=256, unique=True, verbose_name='название города')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['-pk']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        pass


class OFC(BaseModel):
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True, related_name='ofcs',
                             verbose_name='Город')
    address = models.CharField(max_length=256, null=True, blank=True, unique=True, verbose_name='Адрес')
    code = models.CharField(max_length=32, null=True, blank=True, verbose_name='Код')
    is_active = models.BooleanField(default=True, verbose_name='Активность')

    class Meta:
        verbose_name = 'ЦФЗ(Центр Формирования Заказа)'
        verbose_name_plural = 'ЦФЗ(Центр Формирования Заказа)'
        ordering = ['-pk']

    def __str__(self):
        return str(self.address)

    def get_absolute_url(self):
        return self.address


class Period(BaseModel):
    start_date = models.DateField(null=True, blank=True, verbose_name='Начальная дата')
    final_date = models.DateField(null=True, blank=True, verbose_name='Конечная дата')

    class Meta:
        verbose_name = 'Период'
        verbose_name_plural = 'Периоды'
        ordering = ['-pk']

    def __str__(self):
        return f'{self.start_date.strftime("%d.%m.%Y")} - {self.final_date.strftime("%d.%m.%Y")}'

    def get_absolute_url(self):
        pass

    @property
    def get_hours_sum(self):
        return DayHour.objects.filter(day__period=self).aggregate(Sum('hour')).get('hour__sum')

    @property
    def get_executors_count(self):
        return Executor.objects.filter(executor_hours__period=self).distinct().count()


class Day(BaseModel):
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='days', verbose_name='Период')
    date = models.DateField(null=True, blank=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'День'
        verbose_name_plural = 'Дни'
        ordering = ['-pk']

    def __str__(self):
        return self.date.strftime("%d/%m/%Y")

    def get_absolute_url(self):
        pass

    @property
    def get_hours_sum(self):
        return DayHour.objects.filter(day=self).aggregate(Sum('hour')).get('hour__sum')


class Transport(BaseModel):
    name = models.CharField(max_length=256, verbose_name='Название')
    is_own = models.BooleanField(default=False, verbose_name='Собственный')

    class Meta:
        verbose_name = 'Транспорт'
        verbose_name_plural = 'Транспорты'
        ordering = ['-pk']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        pass

    @property
    def get_active_executors_count(self):
        last_periods = Period.objects.all().order_by('-final_date')[:4]
        last_periods = last_periods[::-1]
        executors = Executor.objects.filter(executor_hours__period__in=last_periods, transport=self).distinct()
        return executors.count()


class AdditionalReason(BaseModel):
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Причина для изм. тарифа'
        verbose_name_plural = 'Причины для изм. тарифа'
        ordering = ['-pk']

    def __str__(self):
        return self.description[:20]

    def get_absolute_url(self):
        pass


class Tariff(BaseModel):
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True, blank=True, related_name='tariff',
                                  verbose_name='Транспорт')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='tariff', verbose_name='Период')
    day = models.ForeignKey(Day, on_delete=models.CASCADE, null=True, blank=True, verbose_name='День')
    ofc = models.ForeignKey(OFC, on_delete=models.CASCADE, verbose_name='ЦФЗ')
    additional_reasons = models.ManyToManyField(AdditionalReason, related_name='tariffs')

    amount = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='Сумма')

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
        ordering = ['-pk']

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        pass


class Bicycle(BaseModel):
    code = models.CharField(max_length=256, unique=True, verbose_name='Код велосипеда')

    class Meta:
        verbose_name = 'Велосипед'
        verbose_name_plural = 'Велосипеды'
        ordering = ['-pk']

    def __str__(self):
        return self.code

    def get_absolute_url(self):
        pass

    @property
    def get_executor(self):
        executor = Executor.objects.filter(bicycle=self).first()
        return executor


class CitizenshipType(BaseModel):
    name = models.CharField(max_length=64, verbose_name='Название', unique=True)

    class Meta:
        verbose_name = 'Тип гражданства'
        verbose_name_plural = 'Типы гражданства'
        ordering = ['-pk']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        pass


class Citizenship(BaseModel):
    name = models.CharField(max_length=64, verbose_name='Название', unique=True)

    class Meta:
        verbose_name = 'Гражданство'
        verbose_name_plural = 'Гражданства'
        ordering = ['-pk']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        pass


class SalaryFile(BaseModel):
    pass


class Executor(BaseModel):
    class GenderChoices(models.TextChoices):
        NOT_CHOSEN = 'NOT_CHOSEN', 'Не выбрано'
        MALE = 'MALE', 'Мужской'
        FEMALE = 'FEMALE', 'Женский'

    # code = models.CharField(max_length=64, db_index=True, null=True, blank=True,
    #                         verbose_name='Код ')

    executor_id = models.CharField(max_length=64, unique=True, db_index=True, null=True, blank=True,
                                   verbose_name='Идентификатор')
    last_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='Фамилия')
    first_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='Имя')
    patronymic = models.CharField(max_length=128, null=True, blank=True, verbose_name='Отчество')
    citizenship = models.ForeignKey(Citizenship, on_delete=models.DO_NOTHING, null=True, blank=True,
                                    related_name='executors', verbose_name='Гражданство')
    citizenship_type = models.ForeignKey(CitizenshipType, on_delete=models.DO_NOTHING, null=True, blank=True,
                                         related_name='executors', verbose_name='Тип гражданства')
    INN = models.CharField(max_length=32, null=True, blank=True, verbose_name='ИНН')
    phone_number = models.CharField(max_length=32, null=True, blank=True, verbose_name='Телефон')
    email = models.EmailField(null=True, blank=True, verbose_name='Почта')
    gender = models.CharField(max_length=32, choices=GenderChoices.choices, default=GenderChoices.NOT_CHOSEN,
                              verbose_name='Пол')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    main_contract = models.CharField(max_length=128, null=True, blank=True, verbose_name='Основной контракт')

    OFC = models.ForeignKey(OFC, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name='ЦфЗ')
    education = models.CharField(max_length=256, null=True, blank=True, verbose_name='Образование')

    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='executors', verbose_name='Транспорт')

    curator = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='executors',
                                verbose_name='Куратор')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_terminated = models.BooleanField(default=False, verbose_name='Расторгнут')
    date_terminated = models.DateField(null=True, blank=True, verbose_name='Дата расторжения')
    date_conclusion = models.DateField(null=True, blank=True, verbose_name='Дата заключения')
    partner = models.CharField(max_length=128, null=True, blank=True, verbose_name='Партнер')

    passport_series = models.CharField(max_length=256, null=True, blank=True, verbose_name='Серия и номер паспорта')
    passport_date = models.DateField(null=True, blank=True, verbose_name='Дата выдачи паспорта')
    passport_place = models.CharField(max_length=256, null=True, blank=True, verbose_name='Место выдачи паспорта')

    med_exam_date = models.DateField(null=True, blank=True, verbose_name='Дата медкомиссии')
    individual = models.CharField(max_length=256, null=True, blank=True, verbose_name='Физическое лицо')
    note = models.TextField(null=True, blank=True, verbose_name='Примечание')

    bicycle = models.OneToOneField(Bicycle, on_delete=models.SET_NULL, null=True, blank=True, related_name='executor')

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'
        ordering = ['-pk']

    def __str__(self):
        return self.get_full_name

    def get_absolute_url(self):
        return reverse('app:executor_detail', args=[self.executor_id])

    def get_api_url(self):
        return reverse('app:executor_detail_json', args=[self.executor_id])

    @property
    def get_full_name(self):
        full_name = ''
        if self.last_name:
            full_name += self.last_name
        if self.first_name:
            full_name += ' ' + self.first_name
        if self.patronymic:
            full_name += ' ' + self.patronymic
        return full_name if full_name else '-'

    @property
    def get_whatsapp(self):
        whatsapp = self.contacts.filter(type=Contact.TypeChoices.WHATSAPP).first()
        if whatsapp:
            return whatsapp.identifier
        return None
    @property
    def get_whatsapp_url(self):
        try:
            host_name = socket.gethostname()
            print(host_name)
        except:
            host_name = 'localhost'
        url = f"https://wa.me/{self.get_whatsapp}?text=http://{host_name}" + reverse('app:executor_hours_detail',
                                                                                     args=[self.executor_id])
        return url

    @property
    def get_all_hours_sum(self):
        day_hours = DayHour.objects.filter(executor_hour__executor=self).aggregate(hours_sum=Sum('hour'))
        return day_hours['hours_sum']

    @property
    def get_active_hours_sum(self):
        last_periods = Period.objects.all().order_by('-final_date')[:4].values_list('pk', flat=True)
        day_hours = DayHour.objects.filter(day__period_id__in=last_periods, executor_hour__executor=self).aggregate(
            hours_sum=Sum('hour'))
        return day_hours['hours_sum']


class Contact(BaseModel):
    class TypeChoices(models.TextChoices):
        WHATSAPP = 'whatsapp', 'whatsapp'
        TELEGRAM = 'telegram', 'telegram'
        VK = 'vk', 'vk'
        OK = 'ok', 'ok'

    identifier = models.CharField(max_length=256, verbose_name='Идентификатор')
    executor = models.ForeignKey(Executor, null=True, blank=True, on_delete=models.CASCADE, related_name='contacts',
                                 verbose_name='Исполнитель')
    type = models.CharField(max_length=64, null=True, blank=True, verbose_name='Тип ')

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['type']


class ArchiveFile(BaseModel):
    class TypeChoices(models.TextChoices):
        HOURS = 'hours', 'Часы'
        SALARY = 'salary', 'Зарплата'
        EXECUTOR = 'executor', 'Исполнитель'
        CITY = 'city', 'Город'
        OFC = 'ofc', 'ЦФЗ'
        TRANSPORT = 'transport', 'Транспорт'
        PHONE = 'phone', 'Номера тел.'

    file = models.FileField(upload_to='archive_files', verbose_name='Файл')
    type = models.CharField(max_length=64, choices=TypeChoices.choices, null=True, blank=True, verbose_name='Тип')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    status = models.CharField(max_length=64, choices=StatusChoices.choices, default=StatusChoices.NOT_STARTED,
                              verbose_name='Статус')

    class Meta:
        verbose_name = 'Архивный файл'
        verbose_name_plural = 'Архивные файлы'
        ordering = ['-pk']

    def __str__(self):
        return f'{self.pk} - {self.type}'

    def get_absolute_url(self):
        pass

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class ExecutorHours(BaseModel):
    ofc = models.ForeignKey(OFC, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='executor_hours',
                            verbose_name='ЦФЗ')
    executor = models.ForeignKey(Executor, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='executor_hours',
                                 verbose_name='Исполнитель')
    period = models.ForeignKey(Period, on_delete=models.DO_NOTHING, null=True, blank=True,
                               related_name='executor_hours',
                               verbose_name='Период')
    files = models.ManyToManyField(ArchiveFile, null=True, blank=True,
                                   related_name='executor_hours', verbose_name='Файл')
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='executor_hours')

    class Meta:
        verbose_name = 'Часы исполнителя'
        verbose_name_plural = 'Часы исполнителя'
        ordering = ['-pk']

    def __str__(self):
        return f'{self.pk}'

    def get_absolute_url(self):
        pass

    @property
    def get_hours_sum(self):
        return self.day_hours.aggregate(Sum('hour')).get('hour__sum')

    @property
    def get_days_hour(self):
        pass


class DayHour(BaseModel):
    hour = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name='Часы')
    day = models.ForeignKey(Day, on_delete=models.CASCADE, null=True, blank=True, related_name='executor_hours',
                            verbose_name='День')
    executor_hour = models.ForeignKey(ExecutorHours, on_delete=models.CASCADE, related_name='day_hours',
                                      verbose_name='Часы по дням')

    class Meta:
        verbose_name = 'Часы по дням'
        verbose_name_plural = 'Часы по дням'
        ordering = ['pk']

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        pass


class Profile(BaseModel):
    class RoleChoices(models.TextChoices):
        CURATOR = 'curator', 'Куратор'
        ADMIN = 'admin', 'Админ'
        SUPPORT = 'support', 'Тех. поддержка'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    patronymic = models.CharField(max_length=64, null=True, blank=True, verbose_name='Отчество')
    phone_number = models.CharField(max_length=128, null=True, blank=True, verbose_name='Номер телефона')
    password1 = models.CharField(max_length=128, null=True, blank=True, verbose_name='Текстовый пароль')
    role = models.CharField(max_length=64, choices=RoleChoices.choices, default=RoleChoices.CURATOR,
                            verbose_name='Роль')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        pass

    @property
    def get_full_name(self):
        full_name = ''
        user = self.user
        if user.last_name:
            full_name += user.last_name
        if user.first_name:
            full_name += ' ' + user.first_name
        if self.patronymic:
            full_name += ' ' + self.patronymic

        return full_name if full_name else '-'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
