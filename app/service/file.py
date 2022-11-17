import datetime
from datetime import datetime

import openpyxl
from openpyxl.reader.excel import load_workbook
from openpyxl.utils import get_column_letter

from app.models import Executor, CitizenshipType, Citizenship, OFC


def get_file_data(file):
    workbook = load_workbook(file)
    worksheet = workbook.active
    columns = _get_columns(worksheet)
    print('Columns: ', columns)
    data = _get_data(worksheet, columns)
    return data


def get_executor_file_data(file):
    workbook = load_workbook(file)
    worksheet = workbook.active
    columns = _get_columns(worksheet)
    data = _set_executor_data(worksheet, columns)
    return data


def _get_columns(worksheet) -> dict:
    max_column = worksheet.max_column

    columns = {}
    for column_index in range(1, max_column + 1):
        letter = get_column_letter(column_index)
        value = worksheet[f'{letter}1'].value
        columns[letter] = {
            'index': column_index,
            'value': value
        }
    return columns


def _get_data(worksheet, columns):
    data = []
    max_row = worksheet.max_row
    for row in range(2, max_row + 1):
        data_item = {}
        for column_letter in columns:
            value = columns[column_letter].get('value')
            cell_value = worksheet[f'{column_letter}{row}'].value
            data_item[value] = cell_value
        data.append(data_item)
    print(data)
    return data


# Refactor
def _set_executor_data(worksheet, columns):
    max_row = worksheet.max_row
    for row in range(2, max_row + 1):
        executor = {}
        for column_letter in columns:
            value = columns[column_letter].get('value')
            cell_value = worksheet[f'{column_letter}{row}'].value
            _check_and_save_attribute(executor, value, cell_value)
        _save_executor(executor)


def _save_executor(data: dict):
    executor = Executor.objects.get_or_create(executor_id=data.get('executor_id'))
    if executor[1]:
        executor[0].save()
    executor = executor[0]
    del data['executor_id']
    executor = Executor.objects.filter(pk=executor.id).update(**data)


# Refactor
def _check_and_save_attribute(executor: dict, value, cell_value):
    columns = ['Наименование', 'Код', 'Фамилия', 'Имя', 'Отчество', 'ID', 'Роль', 'Расторгнут', 'Основной договор',
               'Дата расторжения договора', 'Дата заключения договора', 'Партнер', 'Тип гражданства', 'Телефон',
               'Эл почта',
               'Дата медкомиссии', 'Гражданство', 'Дата рождения', 'Образование', 'Пол', 'Серия и номер паспорта',
               'Дата выдачи паспорта', 'Место выдачи паспорта', 'Вакцинирован против COVID19',
               'Дата вакцинации COVID19',
               'Вторая дата вакцинации COVID19', 'Медотвод', 'Дата окончания медотвода', 'Физическое лицо', 'ИНН',
               'Уточнение',
               'Подразделение']

    if 'Наименование' in value:
        pass
        # executor['full_name'] = cell_value
    if 'Фамилия' in value:
        executor['last_name'] = cell_value
    if 'Имя' in value:
        executor['first_name'] = cell_value
    if 'Отчество' in value:
        executor['patronymic'] = cell_value
    if 'ID' == value:
        print(cell_value)
        executor['executor_id'] = cell_value
    if 'Роль' in value:
        if 'курьер' in cell_value.lower():
            executor['role'] = Executor.RoleChoices.COURIER
        else:
            executor['role'] = Executor.RoleChoices.COLLECTOR
    if 'Расторгнут' in value:
        executor['is_terminated'] = True if 'да' in cell_value.lower() else False
    if 'Основной договор' in value:
        executor['main_contract'] = cell_value
    if 'Дата расторжения договора' in value and cell_value:
        executor['date_terminated'] = datetime.strptime(cell_value, '%d.%m.%Y')
    if 'Дата заключения договора' in value:
        executor['date_conclusion'] = datetime.strptime(cell_value, '%d.%m.%Y')
    if 'Партнер' in value:
        executor['partner'] = cell_value
    if 'Тип гражданства' in value:
        executor['citizenship_type'] = CitizenshipType.objects.filter(
            name__icontains='еаэс').first() if cell_value == 1 else CitizenshipType.objects.exclude(
            name__icontains='еаэс').first()
    if 'Телефон' in value:
        executor['phone_number'] = cell_value
    if 'Эл почта' in value:
        executor['email'] = cell_value.strip()
    if 'Дата медкомиссии' in value and cell_value:
        executor['med_exam_date'] = datetime.strptime(cell_value, '%d.%m.%Y')
    if 'Гражданство' in value and cell_value:
        citizenship = Citizenship.objects.get_or_create(name=cell_value)
        if citizenship[1]:
            citizenship[0].save()
        citizenship = citizenship[0]
        executor['citizenship'] = citizenship

    if 'Дата рождения' in value and cell_value:
        executor['birth_date'] = datetime.strptime(cell_value, '%d.%m.%Y')

    if 'Образование' in value:
        executor['education'] = cell_value
    if 'Пол' in value and cell_value:
        executor[
            'gender'] = Executor.GenderChoices.MALE if 'мужской' in cell_value.lower() else Executor.GenderChoices.FEMALE
    if 'Серия и номер паспорта':
        executor['passport_series'] = str(cell_value).strip() if cell_value else cell_value
    if 'Дата выдачи паспорта' in value and cell_value:
        executor['passport_date'] = datetime.strptime(cell_value, '%d.%m.%Y')
    if 'Место выдачи паспорта' in value:
        executor['passport_place'] = cell_value
    if 'Вакцинирован против COVID19' in value:
        pass
        # executor['covid19'] = cell_value
    if 'Вторая дата вакцинации COVID19' in value:
        pass
        # executor['covid19_2'] = cell_value
    if 'Медотвод' in value:
        pass
        # executor['medotvod'] = cell_value

    if 'Дата окончания медотвода' in value:
        pass
        # executor['date_medotvod'] = cell_value
    if 'Физическое лицо' in value:
        executor['individual'] = cell_value
    if 'ИНН' in value:
        executor['INN'] = cell_value
    if 'Уточнение' in value:
        executor['note'] = cell_value
    if 'Подразделение' in value:
        ofc = OFC.objects.get_or_create(address=cell_value)
        if ofc[1]:
            ofc[0].save()
        ofc = ofc[0]
        executor['OFC'] = ofc
