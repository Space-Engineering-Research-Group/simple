import abc
import serial
import micropyGPS

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
            raise RuntimeError(f"Failed _ GPS update_gps: {str(e)}")from e
        

    def get_coordinate_xy(self):
        try:
            self.update_gps()
            latitude = self.__gps.latitude[0]
            longitude = self.__gps.longitude[0]
            if latitude is not None and longitude is not None:
            
                return latitude, longitude

        except serial.SerialException as e:
            raise RuntimeError("GPS communication error")from e
        except Exception as e:
            raise RuntimeError(f"Failed _ GPS xy_coordinates: {str(e)}")from e
        
        return None, None

    def z_coordinate(self):
        try:
            self.update_gps()
            alt = self.__gps.altitude[0]
            #使用するgpsの表記がmだったらそのままで、feetだったらmに直す
            return alt 
        
        except serial.SerialException as e:
            raise RuntimeError("GPS communication error")from e
        except Exception as e:
            raise RuntimeError(f"Failed _ GPS z_coordinate: {str(e)}")from e
    

    def move_direction(self):
        try:
            move_direction = self.__gps.course
            return move_direction
        except AttributeError as e:
                               #move_direction = None,undefined のとき
            raise RuntimeError("Failed to get GPS course.") from e
        except Exception as e:
            raise RuntimeError("Failed _ GPS course.") from e
    
    def delete(self):
        self.sentence = None
        
        if self.__gps_uart:
            try:
                if self.__gps_uart.is_open:
                    self.__gps_uart.close()
            except serial.SerialException as e:
                raise RuntimeError("Failed to close the serial port.") from e