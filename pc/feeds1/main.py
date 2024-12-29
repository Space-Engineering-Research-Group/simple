import xlwings as xw
import os

def feeds1(sheet,data):
    sheet.range("A1").value = "フェーズ"
    sheet.range("B1").value = "時間"
    sheet.range("C1").value = "cds"
    sheet.range("D1").value = "GPS"
    sheet.range("E1").value = "camera"
    sheet.range("F1").value = "motor"
    sheet.range("G1").value = "servo motor"
    sheet.range("H1").value = "xbee"
    sheet.range("I1").value = "故障した部品"
    sheet.range("J1").value = "error"

    Faulty_parts = []
    for index, value in enumerate(data, start=1):
        if data[index - 1] == None:
            a = index - 1
            if a == 2:
                 Faulty_parts.append("cds")
            if a == 3:
                 Faulty_parts.append("GPS")
            if a == 4:
                 Faulty_parts.append("camera")
            if a == 5:
                 Faulty_parts.append("motor")
            if a == 6:
                 Faulty_parts.append("servo motor")
            if a == 7:
                 Faulty_parts.append("xbee")                            

        sheet.range(2, index).value = str(value)

    F_P = ','.join(data)
    sheet.range(2, 9).value = F_P




