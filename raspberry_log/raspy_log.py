import xlwings as xw
import os

import abc

class IXcel(abc.ABC):
    @abc.abstractmethod
    def open_workbook(self):
        pass

    @abc.abstractmethod
    def reconnect_excel(self):
        pass

    @abc.abstractmethod
    def delete(self):
        pass

class Xcel(IXcel):

    def __init__(self):
        self.app = None
        self.workbook = None
        self.sheet = None
    
    def create_new_workbook(self, new_file_path):
        """新しいExcelファイルを作成して保存"""
        self.app = xw.App(visible=True)
        try:
            self.workbook = self.app.books.add()  
            self.sheet = self.workbook.sheets[0]  
            self.workbook.save(new_file_path)   

            return self.sheet
        except Exception as e:
            if self.app:
                self.app.quit()
            raise e
        
    def reconnect_excel(self):
        try:
            app, workbook, sheet = self.open_workbook()
            return app, workbook, sheet
        except Exception as e:
            return e


    def delete(self):
        if hasattr(self, 'workbook') and self.workbook is not None:
            self.workbook.save()
        if hasattr(self, 'workbook') and self.workbook is not None:
            self.workbook.close()  # workbook を閉じる
        if hasattr(self, 'app') and self.app is not None:
            self.app.quit()
            
g = 0  
xcel_judge = False  
while True:        
    try:
        xcel = Xcel()
        g = 0
    except:
        g = g + 1
        if g == 5:
            break
        else:
            xcel_judge = True
            break


def is_row_empty(sheet, row_number): 
    row_values = sheet.range(f"{row_number}:{row_number}").value
    if isinstance(row_values, list):
        return all(value is None for value in row_values)  # すべての値が None なら空行
    return row_values is None

def feeds_1(sheet,data,num):
    #最初num = 4
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 

    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "時間"
        sheet.range(num,3).value = "明るさ"
        sheet.range(num,4).value = "故障した部品"
        sheet.range(num,5).value = "error"

    for index, value in enumerate(data, start=1):
        sheet.range(num+1, index).value = str(value)
        if data[2] == None:
            sheet.range(num+1,4).value = "cds"

    num += 1
    xcel.workbook.save()
    return num                             


def feeds1(sheet,data,num):
    #最初num = 1
    sheet.range(num,1).value = "フェーズ"
    sheet.range(num,2).value = "時間"
    sheet.range(num,3).value = "cds"
    sheet.range(num,4).value = "GPS"
    sheet.range(num,5).value = "camera"
    sheet.range(num,6).value = "motor"
    sheet.range(num,7).value = "servo motor"
    sheet.range(num,8).value = "xbee"
    sheet.range(num,9).value = "故障した部品"
    sheet.range(num,10).value = "error"

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

        sheet.range(num + 1, index).value = str(value)    

    F_P = ','.join(Faulty_parts)
    sheet.range(num+1, 9).value = F_P
    xcel.workbook.save()
    return num + 1


def feeds2(sheet,data,num):
    #最初num = 7 
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 
        
    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "プラン"
        sheet.range(num,3).value = "時間"
        sheet.range(num,4).value = "明るさ"
        sheet.range(num,5).value = "落下判断"
        sheet.range(num,6).value = "使えない部品"
        sheet.range(num,7).value = "error"


    for index, value in enumerate(data, start=1):
        sheet.range(num+1, index).value = str(value)

        if data[3] == None:
            sheet.range(num+1, 6).value = "cds"
    num += 1   
    xcel.workbook.save()      
    return num            

def feeds3(sheet,data,num):
    #以下feeds、最初はわからん
    pass 
    xcel.workbook.save()

def feeds4(sheet,data,num):
    #フェーズ、時間、パラシュート検知,時間、緯度、経度,コーンに対する角度、故障した部品、エラー文
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 
        
    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "時間"
        sheet.range(num,3).value = "パラシュート検知"
        sheet.range(num,4).value = "時間"
        sheet.range(num,5).value = "緯度"
        sheet.range(num,6).value = "経度"
        sheet.range(num,7).value = "コーンに対する角度"
        sheet.range(num,8).value = "故障した部品"
        sheet.range(num,9).value = "error"

    sheet.range(num+1,1).value = "4"

    Faulty_parts = []
    error_list = []
    #フェーズ、フェーズの中のフェーズ、時間、パラシュート検知、故障した部品、エラー文
    if data[1] == 1:
        sheet.range(num+1,2).value = str(data[2])
        sheet.range(num+1,3).value = str(data[3])
        if data[4] is not None and data[5] is not None:
            Faulty_parts.append(data[4])
            error_list.append(data[5])

    #フェーズ、フェーズのフェーズ、時間、緯度、経度、故障した部品、エラー文
    if data[1] == 2:
        sheet.range(num+1,4).value = str(data[2])
        sheet.range(num+1,5).value = str(data[3])
        sheet.range(num+1,6).value = str(data[4])
        if data[5] is not None and data[6] is not None:
            Faulty_parts.append(data[5])
            error_list.append(data[6])

    #フェーズ、フェーズの中のフェーズ、コーンに対する角度、故障した部品、エラー文
    if data[1] == 3:
        sheet.range(num+1,7).value = str(data[2])
        if data[3] is not None and data[4] is not None:
            Faulty_parts.append(data[3])
            error_list.append(data[4])

    F_P = ','.join(Faulty_parts)  
    e_l = ','.join(error_list) 
    sheet.range(num+1,8).value = F_P
    sheet.range(num+1,9).value = e_l
    xcel.workbook.save() 
    return num +1

def feeds5(sheet,data,num):
    #フェーズ、時間、緯度、経度,ゴールまでの距離,時間、進行方向、回転角度、故障した部品、エラー文
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 
        
    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "時間"
        sheet.range(num,3).value = "緯度"
        sheet.range(num,4).value = "経度"
        sheet.range(num,5).value = "ゴールまでの距離"
        sheet.range(num,6).value = "時間"
        sheet.range(num,7).value = "進行方向"
        sheet.range(num,8).value = "回転角度"
        sheet.range(num,9).value = "故障した部品"
        sheet.range(num,10).value = "エラー文"

    sheet.range(num+1,1).value = "5"
    Faulty_parts = []
    error_list = []
    #フェーズ、フェーズの分割番号、時間、緯度、経度,ゴールまでの距離、故障した部品、エラー文
    if data[1] == 1:
        sheet.range(num+1,2).value = str(data[2])
        sheet.range(num+1,3).value = str(data[3])
        sheet.range(num+1,4).value = str(data[4])
        sheet.range(num+1,5).value = str(data[5])
        if data[6] is not None and data[7] is not None:
            Faulty_parts.append(data[6])
            error_list.append(data[7])

     #左からフェーズ、フェーズの分割番号、時間、進行方向、回転角度
    if data[2] == 2:
        sheet.range(num,6).value = str(data[2])
        sheet.range(num,7).value = str(data[3])
        sheet.range(num,8).value = str(data[4])

    else: #最初の緯度経度だけ特別
        for index, value in enumerate(data, start=1):
            sheet.range(num+1, index).value = str(value)

    F_P = ','.join(Faulty_parts)  
    e_l = ','.join(error_list) 
    sheet.range(num+1,9).value = F_P
    sheet.range(num+1,10).value = e_l
    xcel.workbook.save() 
    return num +1        

def feeds6(sheet,data,num):
    #フェーズ、時間、コーン検知、コーンの位置判定、ゴール判定、故障した部品、エラー文
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 
        
    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "時間"
        sheet.range(num,3).value = "コーン検知"
        sheet.range(num,4).value = "コーンの位置判定"
        sheet.range(num,5).value = "ゴール判定"
        sheet.range(num,6).value = "故障した部品"
        sheet.range(num,7).value = "エラー文"

    sheet.range(num+1,1).value = "6"
    Faulty_parts = []
    error_list = []    

    #フェーズ、フェーズの中のフェーズ、時間、コーン検知、故障した部品、エラー文
    if data[1] == 1:
        sheet.range(num+1,2).value = str(data[2])
        sheet.range(num+1,3).value = str(data[3])
        if data[4] is not None and data[5] is not None:
            Faulty_parts.append(data[4])
            error_list.append(data[5])

    #フェーズ、フェーズ中のフェーズ、時間、コーン検出、コーンの位置判定、故障した部品、エラー文
    if data[1] == 2:
        sheet.range(num+1,2).value = str(data[2])
        sheet.range(num+1,3).value = str(data[3])
        sheet.range(num+1,4).value = str(data[4])
        if data[5] is not None and data[6] is not None:
            Faulty_parts.append(data[5])
            error_list.append(data[6])

    #フェーズ、フェーズの中のフェーズ、時間、コーン検知、ゴール判定、故障した部品、エラー文
    if data[1] == 3:
        sheet.range(num+1,2).value = str(data[2])
        sheet.range(num+1,3).value = str(data[3])
        sheet.range(num+1,5).value = str(data[4])
        if data[5] is not None and data[6] is not None:
            Faulty_parts.append(data[5])
            error_list.append(data[6])

    F_P = ','.join(Faulty_parts)  
    e_l = ','.join(error_list) 
    sheet.range(num+1,6).value = F_P
    sheet.range(num+1,7).value = e_l
    xcel.workbook.save() 
    return num +1         

def feeds8(sheet,data,num):
    #左からフェーズ、時間、残り時間  
    sheet.range(num,1).value = "フェーズ"
    sheet.range(num,2).value = "時間"
    sheet.range(num,3).value = "残り時間"

    for index, value in enumerate(data, start=1):
        sheet.range(num+1, index).value = str(value)
    xcel.workbook.save()     

def feeds9(sheet,data,num):
    #フェーズ、時間、故障した部品、エラー文 
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 
        
    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "時間"
        sheet.range(num,3).value = "故障した部品"
        sheet.range(num,4).value = "エラー文"

    for index, value in enumerate(data, start=1):
        sheet.range(num+1, index).value = str(value)   
    xcel.workbook.save()      



#================================= main =============================
class Main():
    def __init__(self,sheet):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "raspy_log:Error"
        self.a = 1

    def main(self,data):
        if xcel_judge == False:
                raise RuntimeError("xcel ins false")
        
        num = 1

        try:
            file_path = r"C:/Users/pekko/OneDrive/ドキュメント/rog.xlsx" #raspyの保存先を入れる。仮の値
            sheet = xcel.create_new_workbook(file_path)
            self.a = 0

        except Exception as e:
                error=f"path cannot--detail{e}"
                self.handle_error(error)
     
        finally:
            if (len(self.error_counts)and self.a==0) or 5 in self.error_counts:
                self.log_errors()


        while True:
            try:

                for i in range(1,9):
                    if data[1] == i:
                        if i == 1:
                            num = feeds1(sheet,data,num)
                        if i == -1:
                            num = feeds_1(sheet,data,num)
                        if i == 2:
                            num = feeds2(sheet,data,num)
                        if i == 3:
                            num = feeds3(sheet,data,num)  
                        if i == 4:
                            num = feeds4(sheet,data,num)
                        if i == 5:
                            num = feeds5(sheet,data,num)
                        if i == 6:
                            num = feeds6(sheet,data,num)
                        if i == 8:
                            num = feeds8(sheet,data,num) 
                        if i == 9:
                            num = feeds9(sheet,data,num)    

                num = num + 1  
                self.a = 0
                break
            except Exception as e:
                error=f"path cannot--detail{e}"
                self.handle_error(error)
     
            finally:
                if (len(self.error_counts)and self.a==0) or 5 in self.error_counts:
                    self.log_errors()

    def handle_error(self, error):
        if str(error) not in self.error_messages:
            self.error_messages.append(str(error))
            self.error_counts.append(1)
        else:
            index = self.error_messages.index(str(error))
            self.error_counts[index] += 1

    def log_errors(self):
        error_list = []
        for count, message in zip(self.error_counts, self.error_messages):
            error_list.append(f"{count}*{message}")
        if self.a == 0:
            self.error_log = "raspy_log:Error--"+",".join(error_list)
        elif 5 in self.error_counts:
            if len(error_list) == 1:
                self.error_log=f"raspy_log:Error--{error_list[0]}"
            else:
                index = self.error_counts.index(5)
                result = error_list[:index] + error_list[index + 1:]
                result = ",".join(result)
                self.error_log = f"raspy_log:Error--{error_list[index]} other errors--{result}"        









    




















