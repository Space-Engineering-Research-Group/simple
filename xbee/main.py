import abc
import serial
import micropyGPS

class IXbee(abc.ABC):
    @abc.abstractmethod
    def xbee_send(self):
        pass

    @abc.abstractmethod
    def xbee_delete(self):
        pass

class Xbee(IXBee):
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

    def xbee_send(date):
        pass

    def xbee_delete(self):
        if self.__xbee_uart and self.__xbee_uart.is_open:
            self.__xbee_uart.close()       

