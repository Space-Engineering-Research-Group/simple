import xlwings as xw
import os

#初めに。
#謝罪があります。
#なぜだか知らないが、どうしても、各ディレクトリに分けて、
#大きなmain文で参照していきながら実行していくという形を取ろうとしても（simple/main.pyみたいなやつ）
#できないので、一つのファイルに、すべてを書きます
#とても見にくいと思いますが、ご了承ください
#申し訳ございませんでした。

#抽象基底かく(feedsのとこ)

class Xcel():

    def __init__(self):
        self.app = None
        self.workbook = None
    
    def open_workbook(self,file_path):
        self.app = xw.App(visible=True)
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"指定されたファイル {file_path} が見つかりません。")
            self.workbook = self.app.books.open(file_path)
            sheet = self.workbook.sheets[0]
            return self.app, self.workbook, sheet
        except Exception as e:
            self.app.quit()
            raise e


    def delete(self):
        if hasattr(self, 'workbook') and self.workbook is not None:
            self.workbook.save()
        if hasattr(self, 'workbook') and self.workbook is not None:
            self.workbook.close()  # workbook を閉じる
        if hasattr(self, 'app') and self.app is not None:
            self.app.quit()

from digi.xbee.devices import XBeeDevice
import json

class XBeeReceiver:
    def __init__(self, port, baud_rate):
        port = "COM3"  # あなたのXBeeモジュールのポートを指定してください
        baud_rate = 9600
        self.device = XBeeDevice(port, baud_rate)

    def open_device(self):
        try:
            self.device.open()
            print("XBee device opened successfully.")
        except Exception as e:
            print(f"Failed to open XBee device: {e}")

    def receive_data(self):
        try:
            print("Waiting for data...")
            while True:
                xbee_message = self.device.read_data()
                if xbee_message is not None:
                    # データをデコード
                    raw_data = xbee_message.data.decode('utf-8')
                    print(f"Received raw data: {raw_data}")

                    try:
                        data = json.loads(raw_data)
                        if isinstance(data, list):  # データがリスト形式か確認
                            return data
                        else:
                            print(f"Received data is not a list")
                    except json.JSONDecodeError:
                        print("Received data is not valid JSON.")
        except Exception as e:
            print(f"Error while receiving data: {e}")


    def close_device(self):
        if self.device is not None and self.device.is_open():
            self.device.close()
            print("XBee device closed.")

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
    return num            

def feeds3(sheet,data,num):
    #以下feeds、最初はわからん
    pass

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
    return num +1

def feeds5(sheet,data,num):














