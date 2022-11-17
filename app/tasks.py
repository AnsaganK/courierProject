from celery import shared_task

from app.models import ArchiveFile, City, OFC
from app.service.file import get_file_data, get_executor_file_data


@shared_task
def create_cities_for_file_task(pk: int):
    file = ArchiveFile.objects.get(pk=pk)
    data = get_file_data(file.file)

    for data_item in data:
        print(data_item)
        city_name = data_item['Город']
        code = data_item['Код']
        address = data_item['Наименование']

        print(city_name)
        if city_name:
            city = City.objects.get_or_create(name=city_name)
            print(city)
            if city[1]:
                city[0].save()
            city = city[0]

            ofc = OFC.objects.get_or_create(address=address, code=code, city=city)
            if ofc[1]:
                ofc[0].save()
            ofc = ofc[0]


@shared_task
def create_executors_for_file_task(pk: int):
    file = ArchiveFile.objects.get(pk=pk)
    data = get_executor_file_data(file.file)
