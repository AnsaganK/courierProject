import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='ofcs', verbose_name='Город')
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
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='Начальная дата')
    final_date = models.DateTimeField(null=True, blank=True, verbose_name='Конечная дата')

    class Meta:
        verbose_name = 'Период'
        verbose_name_plural = 'Периоды'
        ordering = ['-pk']

    def __str__(self):
        return f'{self.start_date.strftime("%d/%m/%Y")} - {self.final_date.strftime("%d/%m/%Y")}'

    def get_absolute_url(self):
        pass


class Day(BaseModel):
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='days', verbose_name='Период')
    date = models.DateField(verbose_name='Дата')

    class Meta:
        verbose_name = 'День'
        verbose_name_plural = 'Дни'
        ordering = ['-pk']

    def __str__(self):
        return self.date.strftime("%d/%m/%Y")

    def get_absolute_url(self):
        pass


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
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE, related_name='tariff', verbose_name='Транспорт')
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


class ExecutorFile(BaseModel):
    pass


class Executor(BaseModel):
    class RoleChoices(models.TextChoices):
        COURIER = 'COURIER', 'Курьер'
        COLLECTOR = 'COLLECTOR', 'Сборщик'

    class GenderChoices(models.TextChoices):
        MALE = 'MALE', 'Мужской'
        FEMALE = 'FEMALE', 'Женский'

    code = models.CharField(max_length=64, unique=True, db_index=True, null=True, blank=True,
                            verbose_name='Идентификатор')
    role = models.CharField(max_length=128, choices=RoleChoices.choices, default=RoleChoices.COURIER,
                            verbose_name='Роль')
    last_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='Фамилия')
    first_name = models.CharField(max_length=128, verbose_name='Имя')
    patronymic = models.CharField(max_length=128, null=True, blank=True, verbose_name='Отчество')
    citizenship = models.ForeignKey(Citizenship, on_delete=models.DO_NOTHING, null=True, blank=True,
                                    related_name='executors', verbose_name='Гражданство')
    citizenship_type = models.ForeignKey(CitizenshipType, on_delete=models.DO_NOTHING, null=True, blank=True,
                                         related_name='executors', verbose_name='Тип гражданства')
    INN = models.CharField(max_length=32, null=True, blank=True, verbose_name='ИНН')
    phone_number = models.CharField(max_length=32, null=True, blank=True, verbose_name='Телефон')
    email = models.EmailField(null=True, blank=True, verbose_name='Почта')
    gender = models.CharField(max_length=32, choices=GenderChoices.choices, verbose_name='Пол')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')

    OFC = models.ForeignKey(OFC, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name='ЦфЗ')
    education = models.CharField(max_length=64, null=True, blank=True, verbose_name='Образование')

    transport = models.ForeignKey(Transport, on_delete=models.DO_NOTHING, null=True, blank=True,
                                  related_name='executors', verbose_name='Транспорт')

    curator = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='executors',
                                verbose_name='Куратор')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'
        ordering = ['-pk']

    def __str__(self):
        return

    @property
    def get_full_name(self):
        full_name = ''
        if self.last_name:
            full_name += self.last_name
        if self.first_name:
            full_name += ' ' + self.first_name
        if self.patronymic:
            full_name += ' ' + self.patronymic
        return full_name if full_name else ' - '


class ArchiveFile(BaseModel):
    class TypeChoices(models.TextChoices):
        SALARY = 'salary', 'Зарплата'
        EXECUTOR = 'executor', 'Исполнитель'
        CITY = 'city', 'Город'
        OFC = 'ofc', 'ЦФЗ'
        TRANSPORT = 'transport', 'Транспорт'

    file = models.FileField(upload_to='archive_files', verbose_name='Файл')
    type = models.CharField(max_length=64, choices=TypeChoices.choices, null=True, blank=True, verbose_name='Тип')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')

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


class Profile(BaseModel):
    class RoleChoices(models.TextChoices):
        CURATOR = 'curator', 'Куратор'
        ADMIN = 'admin', 'Админ'

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
