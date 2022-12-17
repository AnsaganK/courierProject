from celery import shared_task

from app.models import ArchiveFile, City, OFC, StatusChoices
from app.service.file import get_file_data, set_executors_file_data, \
    set_executor_hours_file_data, set_executor_phones_file_data
from utils import set_status


@shared_task
def create_cities_for_file_task(pk: int):
    archive_file = ArchiveFile.objects.get(pk=pk)
    set_status(archive_file, StatusChoices.WAIT)
    data = get_file_data(archive_file.file)
    try:
        for data_item in data:
            city_name = data_item['Город']
            code = data_item['Код']
            address = data_item['Наименование']

            if city_name:
                city = City.objects.get_or_create(name=city_name)
                if city[1]:
                    city[0].save()
                city = city[0]
                ofc = OFC.objects.get_or_create(address=address, code=code, city=city)
                if ofc[1]:
                    ofc[0].save()
        set_status(archive_file, StatusChoices.SUCCESS)
    except:
        set_status(archive_file, StatusChoices.ERROR)


@shared_task
def create_executors_for_file_task(pk: int):
    set_executors_file_data(archive_file_id=pk)


@shared_task
def create_executor_hours_for_file_task(pk: int):
    set_executor_hours_file_data(archive_file_id=pk)


@shared_task
def create_executor_phones_for_file_task(pk: int):
    set_executor_phones_file_data(archive_file_id=pk)
