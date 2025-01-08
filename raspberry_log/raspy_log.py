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

        self.error_counts = []
        self.error_messages = []
        self.error_log = "raspy_log:Error"
        self.a = 1
        self.num = 1

        self.fm1_num_list = []
        self.f2_num_list = []
        self.f4_num_list = []
        self.f5_num_list = []
        self.f6_num_list = []
        self.f7_num_list = []
        self.f9_num_list = []
        self.f10_num_list = []
        self.f11_num_list = []
        self.f12_num_list = []

        try:
            file_path = r"C:/Users/pekko/OneDrive/ドキュメント/rog.xlsx" #raspyの保存先を入れる。仮の値
            self.sheet = self.create_new_workbook(file_path)
            self.a = 0

        except Exception as e:
                error=f"path cannot--detail{e}"
                self.handle_error(error)
                
        finally:
            if (len(self.error_counts)and self.a==0) or 5 in self.error_counts:
                self.log_errors()


    def main(self,data):  

        while True:
            try:
                for i in range(1,9):
                    if data[1] == i:
                        if i == 1:
                            num = self.feeds1(self.sheet,data,self.num)
                        if i == -1:
                            num = self.feeds_1(self.sheet,data,num)
                        if i == 2:
                            num = self.feeds2(self.sheet,data,num) 
                        if i == 4:
                            num = self.feeds4(self.sheet,data,num)
                        if i == 5:
                            num = self.feeds5(self.sheet,data,num)
                        if i == 6:
                            num = self.feeds6(self.sheet,data,num)
                        if i == 8:
                            num = self.feeds8(self.sheet,data,num) 
                        if i == 9:
                            num = self.feeds9(self.sheet,data,num)    
                        if i == 10:
                            num = self.feeds10(self.sheet,data,num) 
                        if i == 11:
                            num = self.feeds11(self.sheet,data,num) 
                        if i == 12:
                            num = self.feeds12(self.sheet,data,num)             

                num = num + 1 
                self.a = 0
                break
            except Exception as e:
                error=f"path cannot--detail{e}"
                self.handle_error(error)
                rapp, rworkbook, rsheet = self.reconnect_excel()
                if rapp is None or rworkbook is None:
                        print("Connection failed. will end")
     
            finally:
                if (len(self.error_counts)and self.a==0) or 5 in self.error_counts:
                    self.log_errors()
            

    
    def create_new_workbook(self, new_file_path):
        """新しいExcelファイルを作成して保存"""
        self.app = xw.App(visible=True)
        try:
            self.workbook = self.app.books.add()  
            self.sheet = self.workbook.sheets[0]  
            self.workbook.save(new_file_path)   

            return self.sheet
        except Exception as e:
            error=f"create_workbook failse--detail{e}"
            self.handle_error(error)
            rapp, rworkbook, rsheet = self.reconnect_excel()
            if rapp is None or rworkbook is None:
                    print("Connection failed. will end")

        finally:
            if (len(self.error_counts)and self.a==0) or 5 in self.error_counts:
                self.log_errors()        
        
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

    def is_row_empty(self,sheet, row_number): 
        row_values = sheet.range(f"{row_number}:{row_number}").value
        if isinstance(row_values, list):
            return all(value is None for value in row_values)  # すべての値が None なら空行
        return row_values is None

    def feeds_1(self,sheet,data,num):
        self.fm1_num_list.append(num)
        if len(self.fm1_num_list) > 2:
            self.fm1_num_list.pop(-1) 

        result = self.is_row_empty(sheet,self.fm1_num_list[0])
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
        self.workbook.save()
        return num                             


    def feeds1(self,sheet,data,num):
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
        self.workbook.save()
        return num + 1


    def feeds2(self,sheet,data,num):
        self.f2_num_list.append(num)
        if len(self.f2_num_list) > 2:
            self.f2_num_list.pop(-1) 
            
        result = self.is_row_empty(sheet,self.f2_num_list[0])
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
        self.workbook.save()      
        return num     



    def feeds4(self,sheet,data,num):
        #フェーズ、時間、パラシュート検知,時間、緯度、経度,コーンに対する角度、故障した部品、エラー文
        self.f4_num_list.append(num)
        if len(self.f4_num_list) > 2:
            self.f4_num_list.pop(-1) 
            
        result = self.is_row_empty(sheet,self.f4_num_list[0])
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
        self.workbook.save() 
        return num +1

    def feeds5(self,sheet,data,num):
        #フェーズ、時間、緯度、経度,ゴールまでの距離,時間、進行方向、回転角度、故障した部品、エラー文
        self.f5_num_list.append(num)
        if len(self.f5_num_list) > 2:
            self.f5_num_list.pop(-1) 
            
        result = self.is_row_empty(sheet,self.f5_num_list[0])
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
        self.workbook.save() 
        return num +1        

    def feeds6(self,sheet,data,num):
        #フェーズ、時間、コーン検知、コーンの位置判定、ゴール判定、故障した部品、エラー文
        self.f6_num_list.append(num)
        if len(self.f6_num_list) > 2:
            self.f6_num_list.pop(-1) 
            
        result = self.is_row_empty(sheet,self.f6_num_list[0])
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
        self.workbook.save() 
        return num +1         

    def feeds8(self,sheet,data,num):
        #左からフェーズ、時間、残り時間  
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "時間"
        sheet.range(num,3).value = "残り時間"

        for index, value in enumerate(data, start=1):
            sheet.range(num+1, index).value = str(value)
        self.workbook.save()    

    def feeds9(self,sheet,data,num):
        #フェーズ、時間、故障した部品、エラー文 
        self.f9_num_list.append(num)
        if len(self.f9_num_list) > 2:
            self.f9_num_list.pop(-1) 
            
        result = self.is_row_empty(sheet,self.f9_num_list[0])
        if result == True:
            sheet.range(num,1).value = "フェーズ"
            sheet.range(num,2).value = "エラー文"

        for index, value in enumerate(data, start=1):
            sheet.range(num+1, index).value = str(value)   
        self.workbook.save()       

    def feeds10(self,sheet,data,num):
        #フェーズ、時間、故障した部品、エラー文 
        self.f10_num_list.append(num)
        if len(self.f10_num_list) > 2:
            self.f10_num_list.pop(-1) 
            
        result = self.is_row_empty(sheet,self.f10_num_list[0])
        if result == True:
            sheet.range(num,1).value = "フェーズ"
            sheet.range(num,2).value = "時間"
            sheet.range(num,3).value = "故障した部品(motor)"
            sheet.range(num,4).value = "エラー文"

        for index, value in enumerate(data, start=1):
            sheet.range(num+1, index).value = str(value)   
        self.workbook.save()   

    def feeds11(self,sheet,data,num):
        #フェーズ、時間、故障した部品、エラー文 
        self.f11_num_list.append(num)
        if len(self.f11_num_list) > 2:
            self.f11_num_list.pop(-1) 
            
        result = self.is_row_empty(sheet,self.f11_num_list[0])
        if result == True:
            sheet.range(num,1).value = "フェーズ"
            sheet.range(num,2).value = "時間"
            sheet.range(num,3).value = "故障した部品(xbee)"
            sheet.range(num,4).value = "エラー文"

        for index, value in enumerate(data, start=1):
            sheet.range(num+1, index).value = str(value)   
        self.workbook.save()            

    def feeds12(self,sheet,data,num):
        #フェーズ、時間、故障した部品、エラー文 
        self.f12_num_list.append(num)
        if len(self.f12_num_list) > 2:
            self.f12_num_list.pop(-1) 
            
        result = self.is_row_empty(sheet,self.f12_num_list[0])
        if result == True:
            sheet.range(num,1).value = "フェーズ"
            sheet.range(num,2).value = "時間"
            sheet.range(num,3).value = "故障した部品(raspy_log)"
            sheet.range(num,4).value = "エラー文"

        for index, value in enumerate(data, start=1):
            sheet.range(num+1, index).value = str(value)   
        self.workbook.save()   
        

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


    




















