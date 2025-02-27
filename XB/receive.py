
#pcで実行
from digi.xbee.devices import XBeeDevice

# TODO: Replace with the serial port where your local module is connected to.

PORT = "COM9"
#ここは挿し口によって変わるよ

# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 9600

def is_integer(s):
    try:
        return int(s)
    except ValueError:
        return s  # 整数に変換できない場合はそのまま返す

def main():
    print(" +-----------------------------------------+")
    print(" | XBee Python Library Receive Data Sample |")
    print(" +-----------------------------------------+\n")

    device = XBeeDevice(PORT, BAUD_RATE)

    try:
        device.open()

        def data_receive_callback(xbee_message):
            data_string = xbee_message.data.decode()
            print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(), data_string))

            # 受信したデータをリストに変換
            data_list_str = data_string.split(',')
            data_list = list(map(is_integer, data_list_str))

            print("Converted list:", data_list)

        device.add_data_received_callback(data_receive_callback)

        print("Waiting for data...\n")
        input()

    finally:
        if device is not None and device.is_open():
            device.close()

if __name__ == '__main__':
    main()