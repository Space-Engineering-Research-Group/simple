

from digi.xbee.devices import XBeeDevice
import abc


class IXBeeDevice(abc.ABC):
    
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod    
    def main(self):
        pass

class XBeeCommunication(IXBeeDevice):

    def __init__(self):
        # TODO: Replace with the serial port where your local module is connected to.
        self.PORT = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AL035I0R-if00-port0"
        # TODO: Replace with the baud rate of your local module.
        self.BAUD_RATE = 9600

        self.DATA_TO_SEND = "Hello XBee!"
        self.REMOTE_NODE_ID = "raspi_node"

# ls -l /dev/serial/by-idして、青い文字をportに入れる

    def send(self,data):
        self.error_counts = []
        self.error_messages = []
        self.error_log="gps Error Log"
        self.a=1
        self.ini=True


        self.DATA_TO_SEND = data
        print(" +--------------------------------------+")
        print(" | XBee Python Library Send Data Sample |")
        print(" +--------------------------------------+\n")

        device = XBeeDevice(self.PORT, self.BAUD_RATE)

        while True:
            try:    
                device.open()

                # Obtain the remote XBee device from the XBee network.
                xbee_network = device.get_network()
                remote_device = xbee_network.discover_device(self.REMOTE_NODE_ID)
                if remote_device is None:
                    print("Could not find the remote device")
                    exit(1)

                print("Sending data to %s >> %s..." % (remote_device.get_64bit_addr(), self.DATA_TO_SEND))

                device.send_data(remote_device, self.DATA_TO_SEND)

                print("Success")
                self.a = 0
                break
            except Exception as e:
                error = f"Failed to open the serial port:: /dev/serial0. Ensure the port is not busy or unavailable.:--detail{e}"
                self.handle_error(error)
                if device is not None and device.is_open():
                    device.close()
            finally:
                if (len(self.error_messages)and self.a==0)or 5 in self.error_counts:
                        if 5 in self.error_counts:
                            if device is not None and device.is_open():
                                device.close()
                        self.xbee_errors()   
                        break  
                
    def log_errors(self):
        list=[]
        for count,message in zip(self.error_counts,self.error_messages):
            list.append(f"{count}*{message}")
        if self.a==0:
            self.error_log=",".join(list)
        elif 5 in self.error_counts:
            index=self.error_counts.index(5)
            result=list[:index]+list[index+1:]
            result=",".join(result)
            self.error_log=f"xbee:Error--{list[index]} other errors--{result}"
        if self.ini==False:    
            raise RuntimeError

    def handle_error(self,error):
        if str(error) not in self.error_messages:
            self.error_messages.append(str(error))
            self.error_counts.append(1)
        else:
            index = self.error_messages.index(str(error))
            self.error_counts[index] += 1
            


if __name__ == '__main__':
    xbee_com = XBeeCommunication()
    xbee_com.main()
