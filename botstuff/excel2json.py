#! python3.6
"""
This script is used for converting excel spreadsheets into json that the bot can read.
An example questions.xlsx is provided.
"""

import json
import openpyxl

if __name__ == '__main__':
    wb = openpyxl.load_workbook('questions.xlsx')
    sheet = wb['Sheet1']
    maxrow = sheet.max_row
    qls = []
    for qrow in sheet['A1':f'F{maxrow}']:

        answls = [str(qrow[1].value), str(qrow[2].value), str(qrow[3].value), str(qrow[4].value)]

        qdict = {
            'question': str(qrow[0].value),
            'options': answls,
            'answer': str(answls[int(qrow[5].value) - 1])
        }

        qls.append(qdict)

    with open('questions.json', 'w', encoding = 'UTF-8') as f:
        f.write(json.dumps(qls, indent = 4))
