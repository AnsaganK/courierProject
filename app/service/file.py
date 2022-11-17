import openpyxl
from openpyxl.reader.excel import load_workbook
from openpyxl.utils import get_column_letter


def get_file_data(file) -> list[dict]:
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


def _set_executor_data(worksheet, columns):
    max_row = worksheet.max_row
    for row in range(2, max_row + 1):
        executor = {}
        for column_letter in columns:
            value = columns[column_letter].get('value')
            cell_value = worksheet[f'{column_letter}{row}'].value
            _check_and_save_attribute(executor, value, cell_value)
        print(executor)


def _check_and_save_attribute(executor, value, cell_value):
    if 'Наименование' in value:
        executor['full_name'] = cell_value
    if 'Фамилия' in value:
        executor['last_name'] = cell_value
    if 'Имя' in value:
        executor['first_name'] = cell_value
    if 'Отчество' in value:
        executor['patronymic'] = cell_value
    if 'ID' in value:
        executor['ID'] = cell_value
    if 'Роль' in value:
        executor['role'] = cell_value
    if 'Расторгнут' in value:
        executor['is_terminated'] = cell_value
    if 'Основной договор' in value:
        executor['base_dogovor'] = cell_value

    if 'Дата расторжения договора' in value:
        executor['date_terminated'] = cell_value
    if 'Дата заключения договора' in value:
        executor['date_created'] = cell_value
    if 'Партнер' in value:
        executor['partner'] = cell_value
    if 'Тип гражданства' in value:
        executor['citizenship_type'] = cell_value
    if 'Телефон' in value:
        executor['phone_number'] = cell_value
    if 'Эл почта' in value:
        executor['email'] = cell_value
    if 'Дата медкомиссии' in value:
        executor['date_med'] = cell_value
    if 'Гражданство' in value:
        executor['citizenship'] = cell_value
    if 'Дата рождения' in value:
        executor['birth_date'] = cell_value

    if 'Образование' in value:
        executor['education'] = cell_value
    if 'Пол' in value:
        executor['gender'] = cell_value
    if 'Серия и номер паспорта' in value:
        executor['serial_number'] = cell_value
    if 'Дата выдачи паспорта' in value:
        executor['date_passport'] = cell_value

    if 'Место выдачи паспорта' in value:
        executor['place_passport'] = cell_value
    if 'Вакцинирован против COVID19' in value:
        executor['covid19'] = cell_value
    if 'Вторая дата вакцинации COVID19' in value:
        executor['covid19_2'] = cell_value
    if 'Медотвод' in value:
        executor['medotvod'] = cell_value

    if 'Дата окончания медотвода' in value:
        executor['date_medotvod'] = cell_value
    if 'Физическое лицо' in value:
        executor['phys'] = cell_value
    if 'ИНН' in value:
        executor['INN'] = cell_value
    if 'Уточнение' in value:
        executor['Note'] = cell_value
    if 'Подразделение' in value:
        executor['OFC'] = cell_value
