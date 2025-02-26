from digi.xbee.devices import XBeeDevice
import abc
from time import sleep,time

class IXBee(abc.ABC):
    @abc.abstractmethod
    def send(self):
        pass

    @abc.abstractmethod
    def log_errors(self):
        pass

    @abc.abstractmethod
    def handle_error(self,error):
        pass

class XBee(IXBee):
    def __init__(self):
        self.error_counts = []
        self.error_messages = []
        self.error_log="XBee Error Log"
        self.a=1
        self.ini=True

        while True:
            try:
                # TODO: Replace with the serial port where your local module is connected to.
                self. PORT = "rasupaioID ls/devのやつ"
                # TODO: Replace with the baud rate of your local module.
                self.BAUD_RATE = 9600
                self.REMOTE_NODE_ID = "raspi_node" 
                 # ls -l /dev/serial/by-id　これをして適宜入れる
                self.device = XBeeDevice(self.PORT, self.BAUD_RATE)
                self.device.open()
                self.xbee_network = self.device.get_network()
                self.remote_device = self.xbee_network.discover_device(self.REMOTE_NODE_ID)
                if self.remote_device is None:
                    print("Could not find the remote device")
                    raise Exception #ここは実験によって変えていく
                
                self.a = 0
                break

            except Exception as e:
                # その他のエラー（MicropyGPS の初期化エラーなど）
                error = f"Failed to _init_ the XBee:--detail{e}"
                self.handle_error(error)
                                    #micropyGPS の設定やデータ受信に問題がある
                        
            finally:
                    if (len(self.error_messages)and self.a==0)or 5 in self.error_counts:
                        if 5 in self.error_counts:
                            self.delete()
                        self.log_errors()   
                        break  
            sleep(1)    

    def send(self,DATA_TO_SEND):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "xbee Error Log"
        self.a = 1

        while True:
            try: 
                data = ",".join(map(str, DATA_TO_SEND)) 
                self.device.send_data(self.remote_device, data)

                self.a = 0
                break

            except Exception as e:
                error = f"Failed to send the XBee:---etail{e}"
                self.handle_error(error)    
                print(e)
            
            finally:
                    if (len(self.error_messages) and self.a == 0) or 5 in self.error_counts:
                        if 5 in self.error_counts:
                                self.delete()
                        self.log_errors()
                        break

    def delete(self):
        if self.device is not None and self.device.is_open():
                self.device.close()

    def log_errors(self):
        error_list = []
        for count, message in zip(self.error_counts, self.error_messages):
            error_list.append(f"{count}*{message}")
        if self.a == 0:
            self.error_log = "xbee:Error--"+",".join(error_list)
        elif 5 in self.error_counts:
            if len(error_list) == 1:
                self.error_log=f"xbee:Error--{error_list[0]}"
            else:
                index = self.error_counts.index(5)
                result = error_list[:index] + error_list[index + 1:]
                result = ",".join(result)
                self.error_log = f"xbee:Error--{error_list[index]} other errors--{result}"
            if self.ini==False:
                raise RuntimeError


    def handle_error(self,error):
        if str(error) not in self.error_messages:
            self.error_messages.append(str(error))
            self.error_counts.append(1)
        else:
            index = self.error_messages.index(str(error))
            self.error_counts[index] += 1
