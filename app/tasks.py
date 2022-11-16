from celery import shared_task

from app.models import ExecutorFile
from app.service.file import get_file_data


@shared_task
def create_cities_for_file_task():
    pass


@shared_task
def create_executors_for_file_task(pk):
    executor_file = ExecutorFile.objects.get(pk=pk)
    data = get_file_data(executor_file.file)
