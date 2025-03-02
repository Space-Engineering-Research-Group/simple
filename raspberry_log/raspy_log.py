import os
import csv

class Xcel():

    def __init__(self):
        self.file_path = None
        self.data = []
        self.file_path = r"/home/spacelab/rog.csv"

    def open_workbook(self, file_path):
        self.file_path = file_path
        try:
            if not os.path.exists(file_path):
                print("新しいファイルを作成")
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    self.writer = csv.writer(file)  # ヘッダー行を追加
                print(f"新しいファイル {file_path} を作成しました。")
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                self.data = list(reader)  # データをself.dataに格納

        except Exception as e:
            raise e

    def is_workbook_closed(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        return False  # CSVファイルは常に開いていると仮定します

    def feeds(self, writer, data):
        if data[0] == -2:
            writer.writerow(["フェーズ","時間","故障した部品","error"])
        if data[0] == -1:
            writer.writerow(["フェーズ", "時間", "明るさ", "明るさの評価", "故障した部品", "error"])
        if data[0] == 1:
            writer.writerow(["フェーズ", "時間", "cds", "GPS", "camera", "motor", "servo", "xbee", "故障した部品", "error"])
        if data[0] == 2:
            writer.writerow(["フェーズ", "時間", "明るさ", "明るさの評価", "故障した部品", "error"])
        if data[0] == 4:
            if data[1] == 1:
                writer.writerow(["フェーズ", "フェーズ中のフェーズ", "時間", "パラシュート検知", "故障した部品", "error"])
            if data[1] == 2:
                writer.writerow(["時間", "緯度", "経度", "故障した部品", "error"])
            if data[1] == 3:
                writer.writerow(["フェーズ", "フェーズ中のフェーズ", "コーンに対する角度"])
        if data[0] == 5:
            if data[1] == 0:
                writer.writerow(["フェーズ","フェーズの中のフェーズ", "時間", "緯度", "経度", "ゴールまでの距離", "進行方向", "回転角度", '故障した部品', 'error'])
            if data[1] == 1:
                writer.writerow(["フェーズ","フェーズの中のフェーズ", "時間", "緯度", "経度", "ゴールまでの距離",'故障した部品', 'error'])
            if data[1] == 2:
                writer.writerow(["フェーズ","フェーズの中のフェーズ", "時間","進行方向", "回転角度"])  
        if data[0] == 6:
            if data[1] == 1:
                writer.writerow(["フェーズ", 'フェーズ中のフェーズ', "時間", "コーン検出", '故障した部品', 'error'])
            if data[1] == 2:
                writer.writerow(["フェーズ", 'フェーズ中のフェーズ', "時間", "コーン検出", "コーンの位置判定", "故障した部品", 'error'])
        if data[0] == 8:
            writer.writerow(["フェーズ", "時間", "残り時間"])
        if data[0] == 9:
            writer.writerow(["フェーズ", "log"])
        if data[0] == 10:
            writer.writerow(["フェーズ", "時間", "故障した部品", "error"])
        if data[0] == 11 or data[0] == 12:
            writer.writerow(["フェーズ", "故障した部品", "error"])

    def xcel(self, data):
        self.open_workbook(self.file_path) # open_workbookを最初に呼び出す

        with open(self.file_path, mode='a', newline='', encoding='utf-8') as file: # 追記モードで開く
            writer = csv.writer(file)
        self.feeds(writer, data)
        writer.writerow(data)