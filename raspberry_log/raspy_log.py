import os
import csv
from time import sleep

class Xcel:
    def __init__(self):
        self.file = None
        self.writer = None
        self.current_phase = None # 現在のフェーズを追跡
        self.current_phase_in = None # 現在のフェーズ中のフェーズを追跡
        self.file_path = r"/home/spacelab/rog.csv"

    def open_workbook(self):
        try:
            if not os.path.exists(self.file_path):
                print("新しいファイルを作成")
            self.file = open(self.file_path, mode='a', newline='', encoding='utf-8')
            self.writer = csv.writer(self.file)
            print(f"ファイル {self.file_path} を開きました。")
        except Exception as e:
            print(f"ファイルを開く際にエラーが発生しました: {e}")
            raise

    def write_header(self, data):
        if data[0] == -2:
            self.writer.writerow(["フェーズ","時間","故障した部品","error"])
        if data[0] == -1:
            self.writer.writerow(["フェーズ", "時間", "明るさ", "明るさの評価", "故障した部品", "error"])
        if data[0] == 1:
            self.writer.writerow(["フェーズ", "時間", "cds", "GPS", "camera", "motor", "servo", "xbee", "故障した部品", "error"])
        if data[0] == 2:
            self.writer.writerow(["フェーズ", "時間", "明るさ", "明るさの評価", "故障した部品", "error"])
        if data[0] == 4:
            if data[1] == 1:
                self.writer.writerow(["フェーズ", "フェーズ中のフェーズ", "時間", "パラシュート検知", "故障した部品", "error"])
            if data[1] == 2:
                self.writer.writerow(["時間", "緯度", "経度", "故障した部品", "error"])
            if data[1] == 3:
                self.writer.writerow(["フェーズ", "フェーズ中のフェーズ", "コーンに対する角度"])
        if data[0] == 5:
            if data[1] == 0:
                self.writer.writerow(["フェーズ","フェーズの中のフェーズ", "時間", "緯度", "経度", "ゴールまでの距離", "進行方向", "回転角度", '故障した部品', 'error'])
            if data[1] == 1:
                self.writer.writerow(["フェーズ","フェーズの中のフェーズ", "時間", "緯度", "経度", "ゴールまでの距離",'故障した部品', 'error'])
            if data[1] == 2:
                self.writer.writerow(["フェーズ","フェーズの中のフェーズ", "時間","進行方向", "回転角度"])  
        if data[0] == 6:
            if data[1] == 1:
                self.writer.writerow(["フェーズ", 'フェーズ中のフェーズ', "時間", "コーン検出", '故障した部品', 'error'])
            if data[1] == 2:
                self.writer.writerow(["フェーズ", 'フェーズ中のフェーズ', "時間", "コーン検出", "コーンの位置判定", "故障した部品", 'error'])
        if data[0] == 8:
            self.writer.writerow(["フェーズ", "時間", "残り時間"])
        if data[0] == 9:
            self.writer.writerow(["フェーズ", "log"])
        if data[0] == 10:
            self.writer.writerow(["フェーズ", "時間", "故障した部品", "error"])
        if data[0] == 11 or data[0] == 12:
            self.writer.writerow(["フェーズ", "故障した部品", "error"])

    def xcel(self, data):
        if not self.file:
            self.open_workbook()
        
        # フェーズが変わった場合のみヘッダーを書き込み
        if data[0] in [4,5,6]:
            if data[1] != self.current_phase_in:
                self.write_header(data)
                self.current_phase_in = data[1]

        else:
            if data[0] != self.current_phase:
                self.write_header(data)
                self.current_phase = data[0]

        self.writer.writerow(data)    