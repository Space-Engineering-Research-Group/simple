import xlwings as xw

def feeds1(sheet,data):
    sheet.range("A4").value = "フェーズ"
    sheet.range("B4").value = "時間"
    sheet.range("C4").value = "明るさ"
    sheet.range("D4").value = "故障した部品"
    sheet.range("E4").value = "error"

    for index, value in enumerate(data, start=1):
        if data[2] == None:
            sheet.range(5,4).value = "cds"
            sheet.range("F4").value = "cdsが壊れている"

        sheet.range(4, index).value = str(value)
