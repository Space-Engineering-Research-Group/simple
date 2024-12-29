import xlwings as xw

def is_row_empty(sheet, row_number): 
    row_values = sheet.range(f"{row_number}:{row_number}").value
    if isinstance(row_values, list):
        return all(value is None for value in row_values)  # すべての値が None なら空行
    return row_values is None


def feeds2(sheet,data):
    result = is_row_empty(sheet,7)
    if result == True:
        sheet.range("A7").value = "フェーズ"
        sheet.range("B7").value = "プラン"
        sheet.range("C7").value = "時間"
        sheet.range("D7").value = "明るさ"
        sheet.range("E7").value = "落下判断"
        sheet.range("F7").value = "使えない部品"
        sheet.range("G7").value = "error"

    for i in range(8,100):#100は適当,意味はなし
        result = is_row_empty(sheet, i)
        if result == True: #空であるか確認

            for index, value in enumerate(data, start=1):
                sheet.range(i, index).value = str(value)

                if data[3] == None:
                    sheet.range(i, 6).value = "cds"
                    sheet.range(i+1, 1).value = "cdsが壊れたので、5分間処理を停止したのち、GPSで高度を取得する"
                else:
                    sheet.range(i+1, 1).value = "明るさが一定値を超えたためGPSを用いた着地判定を始める"











def is_row_empty(self,sheet, row_number): 
    row_values = sheet.range(f"{row_number}:{row_number}").value 
    #その行が空なら、 row_values=Noneになる

    if isinstance(row_values, list): 
        return True
    else:  
        return False
