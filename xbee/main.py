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

class Xbee(IXbee):
    def __init__(self):
        try:
            self.__xbee_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
        except Exception as e:
            # 初期化中にエラーが起きた場合にリソースを解放
            if hasattr(self, '_Gps__xbee_uart') and self.__xbee_uart and self.__xbee_uart.is_open:
                self.__xbee_uart.close()
            raise e  # 再度例外を送出    
    
    def xbee_send(self,data,jude):
        try:
            data = str(data)
            jude = str(jude)
            if not isinstance(data, str):
                raise ValueError("Data must be a string.")

            if self.__xbee_uart and self.__xbee_uart.is_open:
                self.__xbee_uart.write(data.encode('utf-8'))
            else:
                 status = "XBee not connected or not open"

        except Exception as e:
                    status = f"Error: {str(e)}"

        #1_インスタンス化、2_cds、3_sarvo、4_gps、5_camera、6_motor
                    
        finally:
             if "1" in jude:
                  if status:
                      with open('/home/pi/space_data.txt', 'a') as log_file:
                       log_file.write(f" Data: {data} | Status: {status}\n")
                  else:
                      with open('/home/pi/space_data.txt', 'a') as log_file:
                       log_file.write(f" Data: {data}")
                          
                       
                       
            
    def xbee_delete(self):
        if self.__xbee_uart and self.__xbee_uart.is_open:
            self.__xbee_uart.close()      
     

 
