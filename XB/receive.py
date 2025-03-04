#使う際
#行68
# self.PORT = "COM6"   デバイスマネージャーの、ポートからチェック　

#行490
#file_path = r"C:/Users/ookam/OneDrive/log.xlsx" を#はるとのパスにする
#を使うPCのPORTとPATHにする

#word参照
#これはPCで実行する

import xlwings as xw
import os
import win32com.client

class Xcel():

    def __init__(self):
        self.app = None
        self.workbook = None
        self.sheet = None
    
    def open_workbook(self,file_path):
        print("a")
        self.app = xw.App(visible=True)
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"指定されたファイル {file_path} が見つかりません。")
            self.workbook = self.app.books.open(file_path)
            self.sheet = self.workbook.sheets[0]
            return self.app, self.workbook, self.sheet
        
        except Exception as e:
            self.app.quit()
            raise e
        
    def reconnect_excel(self,file_path):
        try:
            app, workbook, sheet = self.open_workbook(file_path)
            return app, workbook, sheet
        except Exception as e:
            print(f"再接続に失敗しました: {e}")
            return None, None, None    
        
    def is_workbook_closed(self,file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        excel = win32com.client.Dispatch('Excel.Application')
        for workbook in excel.Workbooks:
            if workbook.FullName.lower() == os.path.abspath(file_path).lower():
                return False  # File is open
        return True  # File is closed

    def delete(self):
        if hasattr(self, 'workbook') and self.workbook is not None:
            self.workbook.save()
        if hasattr(self, 'workbook') and self.workbook is not None:
            self.workbook.close()  # workbook を閉じる
        if hasattr(self, 'app') and self.app is not None:
            self.app.quit()

from digi.xbee.devices import XBeeDevice
import queue

class Xbee():
    def __init__(self):
        # TODO: Replace with the serial port where your local module is connected to.
        self.PORT = "COM9"
        # TODO: Replace with the baud rate of your local module.
        self.BAUD_RATE = 9600

    def is_integer(self,s):
        try:
            return int(s)
        except ValueError:
            return s  # 整数に変換できない場合はそのまま返す

    def main(self):
        print(" +-----------------------------------------+")
        print(" | XBee Python Library Receive Data Sample |")
        print(" +-----------------------------------------+\n")

        device = XBeeDevice(self.PORT, self.BAUD_RATE)
        data_queue = queue.Queue()

        try:
            device.open()

            def data_receive_callback(xbee_message):
                data_string = xbee_message.data.decode()

                # 受信したデータをリストに変換
                data_list_str = data_string.split(',')
                data_list = list(map(self.is_integer, data_list_str))

                print("Converted list:")
                data_queue.put(data_list)

            device.add_data_received_callback(data_receive_callback)

            print("Waiting for data...\n")
            data = data_queue.get()
            if data:
                return data
            input()


        finally:
            if device is not None and device.is_open():
                device.close()   

def is_row_empty(sheet, num):
    print("空列判定")
    col_values = sheet.range(num,1).value
    print("col_values:")
    if col_values is None:
        print("今から書く列は空白")
        return True  # すべての値が None または空文字列なら空列
    else:
        print(col_values)
        print("今から書く列は空白ではない")
        return False
    
def feeds_2(sheet,data,num):
    #最初num = 7 
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 
        
    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "時間"
        sheet.range(num,3).value = "使えない部品"
        sheet.range(num,4).value = "error"    

    for index, value in enumerate(data, start=1):
        sheet.range(num+1, index).value = str(value)   
    workbook.save()      
    return num         
            
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
        sheet.range(num,4).value = "明るさの評価"
        sheet.range(num,5).value = "故障した部品"
        sheet.range(num,6).value = "error" 

    for index, value in enumerate(data, start=1):
        sheet.range(num+1, index).value = str(value)

    num += 1
    workbook.save()
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
    workbook.save()
    return num 


def feeds2(sheet,data,num):
    #最初num = 7 
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 
        
    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "時間"
        sheet.range(num,3).value = "明るさ"
        sheet.range(num,4).value = "明るさの評価"
        sheet.range(num,5).value = "使えない部品"
        sheet.range(num,6).value = "error"    


    for index, value in enumerate(data, start=1):
        sheet.range(num+1, index).value = str(value)   
    workbook.save()      
    return num          


def feeds4(sheet,data,num):
    #フェーズ、時間、パラシュート検知,時間、緯度、経度,コーンに対する角度、故障した部品、エラー文
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 
        
    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "時間1"
        sheet.range(num,3).value = "パラシュート検知"
        sheet.range(num,4).value = "時間2"
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
    workbook.save() 
    return num 

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
        sheet.range(num,6).value = "進行方向"
        sheet.range(num,7).value = "回転角度"
        sheet.range(num,8).value = "故障した部品"
        sheet.range(num,9).value = "エラー文"

    sheet.range(num+1,1).value = "5"
    Faulty_parts = []
    error_list = []
    
    if data[1] == 0:
        #フェーズ、フェーズの中のフェーズ、時間、緯度、経度,ゴールまでの距離,進行方向、回転角度、故障した部品、エラー文
        sheet.range(num+1,2).value = str(data[2])
        sheet.range(num+1,3).value = str(data[3])
        sheet.range(num+1,4).value = str(data[4])
        sheet.range(num+1,5).value = str(data[5])
        sheet.range(num+1,6).value = str(data[6])
        sheet.range(num+1,7).value = str(data[7])
        if data[8] is not None and data[9] is not None:
            Faulty_parts.append(data[8])
            error_list.append(data[9])

     ##左からフェーズ、フェーズの分割番号、時間、緯度、経度,ゴールまでの距離、故障した部品、エラー文
    if data[1] == 1:
        sheet.range(num+1,2).value = str(data[2])
        sheet.range(num+1,3).value = str(data[3])
        sheet.range(num+1,4).value = str(data[4])
        sheet.range(num+1,5).value = str(data[5])
        if data[6] is not None and data[7] is not None:
            Faulty_parts.append(data[6])
            error_list.append(data[7])

    if data[1] == 2:#左からフェーズ、フェーズの分割番号、時間、進行方向、回転角度  
        sheet.range(num+1,2).value = str(data[2])
        sheet.range(num+1,6).value = str(data[3])
        sheet.range(num+1,7).value = str(data[4])

    F_P = ','.join(Faulty_parts)  
    e_l = ','.join(error_list) 
    sheet.range(num+1,8).value = F_P
    sheet.range(num+1,9).value = e_l
    workbook.save() 
    return num     

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
    workbook.save() 
    return num  

def feeds8(sheet,data,num):
    #左からフェーズ、時間、残り時間  
    sheet.range(num,1).value = "フェーズ"
    sheet.range(num,2).value = "時間"
    sheet.range(num,3).value = "残り時間"

    for index, value in enumerate(data, start=1):
        sheet.range(num+1, index).value = str(value)
    workbook.save()     
    return num

def feeds9(sheet,data,num):
    #feeds,nlog
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 
    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "nlog"
        sheet.range(num,2).value = "words"

    for index, value in enumerate(data, start=1):
        sheet.range(num+1, index).value = str(value)   
    workbook.save()      
    return num


def feeds10(sheet,data,num):
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
    workbook.save()     
    return num 

def feeds11(sheet,data,num):
    #フェーズ、故障した部品、エラー文 
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 
        
    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "故障した部品"
        sheet.range(num,3).value = "エラー文"

    for index, value in enumerate(data, start=1):
        sheet.range(num+1, index).value = str(value)   
    workbook.save()     
    return num 

def feeds12(sheet,data,num):
    #フェーズ、故障した部品、エラー文 
    num_list = []
    num_list.append(num)
    if len(num_list) > 2:
        num_list.pop(-1) 
        
    result = is_row_empty(sheet,num_list[0])
    if result == True:
        sheet.range(num,1).value = "フェーズ"
        sheet.range(num,2).value = "故障した部品"
        sheet.range(num,3).value = "エラー文"

    for index, value in enumerate(data, start=1):
        sheet.range(num+1, index).value = str(value)   
    workbook.save()     
    return num 


#ここからがやっとmainだぜっ
#================================= main =============================
import keyboard
print("プログラムを開始します")
try:
    print("通信中...")
    xcel = Xcel()
    xbee = Xbee()
    num = 1
     #初めのfeeds
    i = 1
    print("インスタンス化が完了")
    #はるとのパス
    file_path = r"C:/Users/pekko/OneDrive/ドキュメント/rog.xlsx"
    #ゆうまのパス
    # file_path = r"C:/Users/ookam/OneDrive/log.xlsx"

    app, workbook, sheet = xcel.open_workbook(file_path)

except FileNotFoundError as e:
    print(f"エラー: {e}")
except Exception as e:
    print(f"予期しないエラー発生: {e}")    


while True:
    try:
        data = xbee.main()
        if xcel.is_workbook_closed(file_path):
            #閉じていたら
            print("Excelが閉じられています。再接続します。")
            app, workbook, sheet = xcel.reconnect_excel(file_path)
            if app is None or workbook is None:
                print("Excelへの再接続に失敗しました。終了します。")
                break    
        else:#開いていたら
            print("Excelが開かれています。")
            pass    

        if data[0] != i:
            num += 2
            print("切り替わる")#以下の判断で使うため、ここになる   

        for i in range(1,13):
            if data[0] == i:
                if i == -2:
                    num = feeds_2(sheet,data,num)
                    break
                if i == 1:
                    num = feeds1(sheet,data,num)
                    break
                if i == -1:
                    num = feeds_1(sheet,data,num)
                    break
                if i == 2:
                    num = feeds2(sheet,data,num) 
                    break 
                if i == 4:
                    num = feeds4(sheet,data,num)
                    break
                if i == 5:
                    num = feeds5(sheet,data,num)
                    break
                if i == 6:
                    num = feeds6(sheet,data,num)
                    break
                if i == 8:
                    num = feeds8(sheet,data,num)  
                    break
                if i == 9:
                    num = feeds9(sheet,data,num) 
                    break  
                if i == 10:
                    num = feeds10(sheet,data,num)  
                    break     
                if i == 11:
                    num = feeds11(sheet,data,num)  
                    break    
                if i == 12:
                    num = feeds12(sheet,data,num)  
                    break     
        num += 1

        if keyboard.is_pressed('d'):
            try:
                xcel.delete()
                print("xcelとxbees消去完了")
            except Exception as e:
                print(f"閉じることができなかった{e}")

    except Exception as e:
        print(f"エラー発生: {e}")
        print("再接続します")
        app, workbook, sheet = xcel.reconnect_excel(file_path)
        if app is None or workbook is None:
            print("Excelへの再接続に失敗しました。終了します。")
            break     

print("任務完了しました")