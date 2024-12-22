import abc
import serial
import micropyGPS
import math
import time


class IGps(abc.ABC):
    @abc.abstractmethod
    def update_gps(self):
        pass

    @abc.abstractmethod
    def get_coordinate_xy(self):
        pass
    
    @abc.abstractmethod
    def z_coodinate(self):
        pass
    
    @abc.abstractmethod
    def move_direction(self):
        pass
    
    @abc.abstractmethod
    def delete(self):
        pass


class Gps(IGps):
    def __init__(self):
        try:
            self.__gps_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
            self.__gps = micropyGPS.MicropyGPS(9, "dd")
        except serial.SerialException as e:
             # シリアルポートが開けなかった場合
             if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                 self.__gps_uart.close()
                 raise RuntimeError("Failed to open the serial port:: /dev/serial0. Ensure the port is not busy or unavailable.") from e
                                     #ポートがビジー状態または存在しない
        except Exception as e:
          # その他のエラー（MicropyGPS の初期化エラーなど）
             if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                 self.__gps_uart.close()
                 raise RuntimeError("Failed to _init_ the GPS") from e
                                    #micropyGPS の設定やデータ受信に問題がある
                                    #どこでエラーが起きているかが明確であるため、{e}はしない
    
        self.prev_altitude = None
        self.prev_time = None

    
    def update_gps(self):
        try:
            self.sentence = self.__gps_uart.readline()
            
            if self.sentence:
                for x in self.sentence.decode('ascii', errors='ignore'):
                    self.__gps.update(x)  

        except serial.SerialException as e:
            raise RuntimeError("GPS communication error")from e
        except Exception as e:
            raise RuntimeError(f"Failed _ GPS update_gps: {str(e)}")
        

    def get_coordinate_xy(self):
        try:
            lali = [] #latitude_list
            loli = [] #longitude_list
            self.update_gps()
            for i in range(30):
                start_time = time.time()
                while True:
                    current_time = time.time()

                    latitude = self.__gps.latitude[0]
                    longitude = self.__gps.longitude[0]
                    if latitude is None and longitude is None:      
                        raise ValueError("lat , lon is None")
                    
                    time_difference = current_time - start_time

                    if time_difference > 0.11:
                        m_latitude, m_longitude = self.dms_to_decimal(latitude,longitude)
                        if m_latitude is None and m_longitude is None:
                            raise ValueError("m_lat , m_lon is None")
            
                        lali.append(m_latitude)
                        loli.append(m_longitude)
                        break

            ave_lat = sum(lali)/len(lali)
            ave_lon = sum(loli)/len(loli)               
            return ave_lat, ave_lon

        except serial.SerialException as e:
            raise RuntimeError("GPS communication error")
        except Exception as e:
            raise RuntimeError(f"Failed _ GPS xy_coordinates: {str(e)}")
        

    def z_coordinate(self):
        try:
            self.update_gps()
            alt = self.__gps.altitude[0]
            #使用するgpsの表記がmだったらそのままで、feetだったらmに直す
            return alt 
        
        except serial.SerialException as e:
            raise RuntimeError("GPS communication error")
        except Exception as e:
            raise RuntimeError(f"Failed _ GPS z_coordinate: {str(e)}")
    

    def move_direction(self):
        try:
            move_direction = self.__gps.course
            return move_direction
        except AttributeError as e:
                               #move_direction = None,undefined のとき
            raise RuntimeError("Failed to get GPS course.") 
        except Exception as e:
            raise RuntimeError("Failed _ GPS course.") 
    
    def delete(self):
        self.sentence = None
        
        if self.__gps_uart:
            try:
                if self.__gps_uart.is_open:
                    self.__gps_uart.close()
            except serial.SerialException as e:
                raise RuntimeError("Failed to close the serial port.") 

    def dms_to_decimal(self,lat,lon):

            # 度と分に分割する
        lat_degrees = int(lat / 100)  # 整数部分（度）
        lat_minutes = lat % 100  # 小数部分（分）

        lon_degrees = int(lon / 100)  # 整数部分（度）
        lon_minutes = lon % 100  # 小数部分（分）

        # 10進法に変換
        m_latitude = lat_degrees + lat_minutes / 60
        m_longitude = lon_degrees + lon_minutes / 60

        return m_latitude, m_longitude
