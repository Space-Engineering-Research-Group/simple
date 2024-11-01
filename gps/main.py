import abc
import serial
import micropyGPS
import time

class IGps(abc.ABC):
    @abc.abstractmethod
    def update_gps(self):
        pass

    @abc.abstractmethod
    def get_coordinate_xy(self):
        pass
    
    @abc.abstractmethod
    def get_speed_z(self):
        pass
    
    @abc.abstractmethod
    def move_direction(self):
        pass
    
    @abc.abstractmethod
    def delete(self):
        pass


class Gps(IGps):
    def __init__(self):
        # ポート設定
        self.__gps_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
        self.__gps = micropyGPS.MicropyGPS(9, "dd")

        # データバッファ
        self.__data_buffer = ""
        self.__dataz_buffer = ""
        
        # 前回の高度と時刻
        self.prev_altitude = None
        self.prev_time = None

    def update_gps(self):
        try:
            sentence = self.gps_uart.readline()  # GPSデバイスから1行のデータを読み取る
            if sentence:
                for x in sentence.decode('ascii', errors='ignore'):
                    self.gps.update(x)  # 1文字をupdateメソッドに渡して解析

        except serial.SerialException as e:
            print(f"GPS通信エラー: {e}")  # シリアル通信に関するエラーを処理
        except Exception as e:
            print(f"GPS更新エラー: {e}")  # その他のエラーを処理



    def get_coordinate_xy(self):
        try:
            self.update_gps()
            latitude = self.__gps.latitude[0]
            longitude = self.__gps.longitude[0]
            if latitude is not None and longitude is not None:
                print(f'Latitude: {latitude}, Longitude: {longitude}')
                return latitude, longitude

        except serial.SerialException as e:
            print(f"GPS communication error: {e}")
        except Exception as e:
            print(f"GPS error: {e}")
        
        return None, None

    def get_speed_z(self):
        try:
            self.update_gps()
            altitude = self.__gps.altitude[0]
            current_time = time.time()
                                
            if altitude is not None:
                 if self.prev_altitude is not None and self.prev_time is not None:
                        # z座標の速度を計算 (m/s)
                    time_diff = current_time - self.prev_time
                    if time_diff > 0:
                        speed_z = (altitude - self.prev_altitude) / time_diff
                            # print(f"Vertical Speed (Z-axis): {speed_z} m/s")
                        self.prev_altitude = altitude
                        self.prev_time = current_time
                        return speed_z
                    else:
                        # 初回のデータ取得
                     self.prev_altitude = altitude
                     self.prev_time = current_time
                                
        except serial.SerialException as e:
            print(f"GPS communication error: {e}")
        except Exception as e:
            print(f"GPS error: {e}")
        
        return None
    
  #gpsのデータは、役割が違う改行された複数の文で構成されているため、改行ごとにわける必要がある
   #受信側のコードは別にある

    def move_direction(self):
        gps.course  使う
        return direction
    

    
    #どれを基準とした方向なのかを聴く
    #真北を0度、基準としている
    #一般的なgpsと同じ
    

    def delete(self):
        self.__sentence = None
        if self.__gps_uart and self.__gps_uart.is_open:
            self.__gps_uart.close()
        if self.__xbee_uart and self.__xbee_uart.is_open:
            self.__xbee_uart.close()    