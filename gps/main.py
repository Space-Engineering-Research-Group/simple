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
        except Exception as e:
            # 初期化中にエラーが起きた場合にリソースを解放
            if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                self.__gps_uart.close()   
        
        self.prev_altitude = None
        self.prev_time = None

    
    def update_gps(self):
        try:
            self.sentence = self.__gps_uart.readline()
            
            if self.sentence:
                for x in self.sentence.decode('ascii', errors='ignore'):
                    self.__gps.update(x)  

        except serial.SerialException as e:
            print(f"GPS communication error: {e}")  
        except Exception as e:
            print(f"GPS update error: {e}")  


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

    def z_coordinate(self):
        try:
            self.update_gps()
        except serial.SerialException as e:
            print(f"gps comminucation error:{e}")    
        alt = self.__gps.altitude[0]
        return alt 
    
    def move_direction(self):
        move_direction = self.__gps.course
        
        return move_direction
    
    def delete(self):
        self.sentence = None
        if self.__gps_uart and self.__gps_uart.is_open:
            self.__gps_uart.close() 
            