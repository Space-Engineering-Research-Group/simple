#注意。
#このコードはラズパイ上では動かさず、パソコンで動かすコードである
#一応git_hubに保存しているが、後に消す

import serial
import keyboard
import os

def receive_xbee_data():
    if os.path.exists("/dev/serial0"):
        try:
            xbee_serial = serial.Serial(port='/dev/serial0', baudrate=9600, timeout=10)
            #受信データをファイルに保存
            faile = input("保存するファイルのパスを書いてください。ゆうまのパソコンなら１を押して")
            if faile == "1":
                faile = "C:\Users\ookam\razpai_faile.txt"

            print("運行が終わった際、ctr_Cで終了させて")

            print("XBeeからのデータ受信を開始します...")

            with open(faile, 'a') as Linux_file:  
                while True:
                    #返される値が 0 なら、受信バッファにデータはないことを意味する
                    if xbee_serial.in_waiting > 0:  
                        data = xbee_serial.readline().decode('utf-8').strip()  
                        print(f"data:{data}")
                        Linux_file.write(data + "\n") 

                    if keyboard.is_pressed('ctrl+c'):  
                        print("終わり")
                        break      

        except Exception as e:
            print(f"エラーが発生しました: {e}")

        finally:
            if 'xbee_serial' in locals() and xbee_serial.is_open:
                xbee_serial.close()
                print("シリアルポートを閉じました。")
    else:
        print("ポートが存在しない")              
receive_xbee_data()
