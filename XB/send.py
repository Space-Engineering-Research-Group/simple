

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

# ls -l /dev/serial/by-id

    def main(self):
        print(" +--------------------------------------+")
        print(" | XBee Python Library Send Data Sample |")
        print(" +--------------------------------------+\n")

        device = XBeeDevice(self.PORT, self.BAUD_RATE)

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

        finally:
            if device is not None and device.is_open():
                device.close()


if __name__ == '__main__':
    xbee_com = XBeeCommunication()
    xbee_com.main()
