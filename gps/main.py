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
        try:
            self.__gps_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
            self.__xbee_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
            self.__gps = micropyGPS.MicropyGPS(9, "dd")
        except Exception as e:
            # 初期化中にエラーが起きた場合にリソースを解放
            if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                self.__gps_uart.close()
            if hasattr(self, '_Gps__xbee_uart') and self.__xbee_uart and self.__xbee_uart.is_open:
                self.__xbee_uart.close()
            raise e  # 再度例外を送出    
        
        self.prev_altitude = None
        self.prev_time = None

    def update_gps(self):
        try:
            self.sentence = self.__gps_uart.readline()
            
            if self.sentence:
                for x in self.sentence.decode('ascii', errors='ignore'):
                    self.gps.update(x)  

        except serial.SerialException as e:
            print(f"GPS通信エラー: {e}")  
        except Exception as e:
            print(f"GPS更新エラー: {e}")  



    def get_coordinate_xy(self):
        try:
            self.update_gps()
            latitude = self.__gps.latitude[0]
            longitude = self.__gps.longitude[0]
            if latitude is not None and longitude is not None:
            
                return latitude, longitude

        except serial.SerialException as e:
            print(f"GPS communication error: {e}")
        except Exception as e:
            print(f"GPS error: {e}")
        
        return None, None

    def get_speed_z(self):
        try:
            self.update_gps()
        except Exception as e:
            print(f"Error updating GPS: {e}")

            altitude = self.__gps.altitude[0] if self.__gps.altitude else None
            if altitude is None:
                raise ValueError("altitude is None.")
            current_time = time.time()

            if altitude is not None:                    
                if self.prev_altitude is not None and self.prev_time is not None:
                    raise ValueError("self.prev_altitude is None and self.prev_time is None.")
                        
                time_diff = current_time - self.prev_time
                if time_diff > 0:
                    speed_z = (altitude - self.prev_altitude) / time_diff
                            
                    self.prev_altitude = altitude
                    self.prev_time = current_time
                    return speed_z
                else:
                    
                    self.prev_altitude = altitude
                    self.prev_time = current_time
                                
        except serial.SerialException as e:
            print(f"GPS communication error: {e}")
        except Exception as e:
            print(f"GPS error: {e}")
        
        return None
    
    def move_direction(self):
        move_direction = self.__gps.course
        return move_direction
    
    def delete(self):
        self.sentence = None
        if self.__gps_uart and self.__gps_uart.is_open:
            self.__gps_uart.close()
        if self.__xbee_uart and self.__xbee_uart.is_open:
            self.__xbee_uart.close()    
            