import xlwings as xw
import os
import time

def feeds1(app, workbook, sheet,data):
    sheet.range("A1").value = "フェーズ"
    sheet.range("B1").value = "時間"

