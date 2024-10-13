import serial
import abc

class IXbee(abc.ABC):
    @abc.abstractmethod
    def receive(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass

class XBee(IXbee):
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=10):
        self.__xbee_uart = serial.Serial(port, baudrate, bytesize=serial.EIGHTBITS, timeout=timeout)


    def receive(self):
        try:
            
                # XBeeからのデータがあるか確認
            if self.__xbee_uart.in_waiting:
                    # データを受信してデコード
                data = self.__xbee_uart.readline().decode('utf-8').strip()
                print(f"受信したデータ: {data}")
                self.save_to_file(data)
                return data
        except Exception as e:
            print(f"XBee受信エラー: {e}")

    def save_to_file(self, data):
        try:
            with open('gpsdata', 'a') as file:
                file.write(f"{data}\n")
            print(f"データをファイルに保存しました: {data}")
        except Exception as e:
            print(f"ファイル保存エラー: {e}")

    def close(self):
        # シリアル接続を閉じる
        if self.__xbee_uart:
            self.__xbee_uart.close()
            print("XBee接続を終了しました。")

# main
receiver = XBee('/dev/ttyUSB0', 9600)
try:
    while True:
        data = receiver.receive()
        if data:
            print(f"処理されたデータ: {data}")
        else:
            print('gps data is nothing')    
except KeyboardInterrupt:
    print("プログラムが中断されました。")
except serial.SerialException as e:
    print(f"シリアル通信エラー: {e}")
except Exception as e:
    print(f"予期しないエラー: {e}")    

finally:
    receiver.close()
