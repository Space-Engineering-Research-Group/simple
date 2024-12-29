import abc
import json
from digi.xbee.devices import XBeeDevice
from serial import SerialException
from digi.xbee.exception import XBeeException,TransmitException


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
                self.PORT = "COM3" 
                self.BAUD_RATE = 9600
                self.DEVICE_ID = "00:13:A2:00:41:59:5C:54"  #adles
                self.device = XBeeDevice(self.PORT, self.BAUD_RATE)

            except SerialException as e:
                error = f"port erorr-- detail {e}"  
                self.handle_error(error) 

            except XBeeException as e:  
                error = f"xbee error-- detail {e}"  
                self.handle_error(error) 

            except Exception as e:
                error = f"other error-- detail {e}"  
                self.handle_error(error) 

            finally:
                if (len(self.error_messages) and self.a == 0) or 5 in self.error_counts:
                    self.log_errors()
                    if 5 in self.error_counts: 
                        if hasattr(self, 'device') and self.device and self.device.is_open:
                            self.device.close()
                    break    

    def xbee_send(self,data):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "xbee:Error"
        self.a = 1
        while True:
            try:
                self.device.open()
                json_data = json.dumps(data)
                self.device.send_data_remote(self.DEVICE_ID, json_data.encode())
                self.a = 0
            except TransmitException as e: 
                error = f"Data transmission failed-- detail {e}"  
                self.handle_error(error)    
            except XBeeException as e:
                error = f"Common errors related to XBee devices-- detail {e}"  
                self.handle_error(error) 
            except SerialException as e:
                error = f"The serial port cannot be opened or a communication error has occurred-- detail {e}"  
                self.handle_error(error) 
            except TypeError as e:
                error = f"JSON data conversion failed-- detail {e}"  
                self.handle_error(error)        
            except Exception as e:
                error = f"other error-- detail {e}"  
                self.handle_error(error)   
            finally:
                if (len(self.error_messages) and self.a == 0) or 5 in self.error_counts:
                    if 5 in self.error_counts: 
                        if hasattr(self, 'device') and self.device and self.device.is_open:
                            self.device.close()
                    self.log_errors()
                    break         
                
    def xbee_delete(self):
        if self.device.is_open:
            self.device.close()  


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
     




