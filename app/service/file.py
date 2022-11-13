import openpyxl


def read_excel(file):
    data = openpyxl.load_workbook(file)
    print(data)
