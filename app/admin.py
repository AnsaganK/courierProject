from django.contrib import admin

from app.models import City, OFC, Transport, AdditionalReason, Tariff, Bicycle, Citizenship, Executor, Profile, \
    ExecutorHours, Period, Day, DayHour, ArchiveFile


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'short_name']
    list_editable = ['short_name']


@admin.register(OFC)
class OFCAdmin(admin.ModelAdmin):
    list_display = ['pk', 'address']


@admin.register(Transport)
class Transport(admin.ModelAdmin):
    list_display = ['pk', 'name', 'is_own']


@admin.register(AdditionalReason)
class AdditionalReasonAdmin(admin.ModelAdmin):
    list_display = ['pk', 'description']


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ['pk', 'day', 'amount']


@admin.register(Bicycle)
class BicycleAdmin(admin.ModelAdmin):
    list_display = ['pk', 'code']


@admin.register(Citizenship)
class CitizenshipAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']


@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    list_display = ['pk']


@admin.register(ExecutorHours)
class ExecutorHoursAdmin(admin.ModelAdmin):
    list_display = ['pk']


@admin.register(DayHour)
class DayHourAdmin(admin.ModelAdmin):
    list_display = ['pk']


@admin.register(ArchiveFile)
class ArchiveFileAdmin(admin.ModelAdmin):
    list_display = ['pk']


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['pk', 'start_date', 'final_date']


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ['pk']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['pk', 'role']
