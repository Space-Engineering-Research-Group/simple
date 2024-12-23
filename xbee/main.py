import abc
import serial
import micropyGPS
from time import sleep

class IXbee(abc.ABC):
    @abc.abstractmethod
    def xbee_send(self):
        pass

    @abc.abstractmethod
    def xbee_delete(self):
        pass

class Xbee(IXbee):
    def __init__(self):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "xbee:Error"
        self.a = 1
        while True:
            try:
                self.__xbee_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
                self.a = 0
                break

            except Exception as e:
                # 初期化中にエラーが起きた場合にリソースを解放
                if hasattr(self, '_Gps__xbee_uart') and self.__xbee_uart and self.__xbee_uart.is_open:
                    self.__xbee_uart.close()
                error = f"False to init-- detail {e}"  
                self.handle_error(error) 
            finally:
                if (len(self.error_messages) and self.a == 0) or 5 in self.error_counts:
                    self.log_errors()
                    break
     
    def xbee_send(self,data,jude):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "xbee:Error"
        self.a = 1
        while True:
            #まだ完成していない、、、考え中 　selfa=0 を書くこと

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
                            log_file.write(f" Data: {data}, | Status: {status}\n")
                    else:
                        with open('/home/pi/space_data.txt', 'a') as log_file:
                            log_file.write(f" Data: {data}")
                          
                       
                       
            
    def xbee_delete(self):
        if self.__xbee_uart and self.__xbee_uart.is_open:
            self.__xbee_uart.close()      


    def handle_error(self,error):
        if str(error) not in self.error_messages:
            self.error_messages.append(str(error))
            self.error_counts.append(1)
        else:
            index = self.error_messages.index(str(error))
            self.error_counts[index] += 1


    def log_errors(self):
        list=[]
        for count,message in zip(self.error_counts,self.error_messages):
            list.append(f"{count}*{message}")
        if self.a==0:
            self.error_log=",".join(list)
        elif 5 in self.error_counts:
            if len(list) == 1:
                self.error_log=f"cds:Error--{list[0]}"
            else:
                index=self.error_counts.index(5)
                result=list[:index]+list[index+1:]
                result=",".join(result)
                self.error_log=f"cds:Error--{list[index]} other errors--{result}"
            raise RuntimeError        
     

 
