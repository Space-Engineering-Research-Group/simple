from digi.xbee.devices import XBeeDevice
import json

class XBeeReceiver:
    def __init__(self, port, baud_rate):
        port = "COM3"  # あなたのXBeeモジュールのポートを指定してください
        baud_rate = 9600
        self.device = XBeeDevice(port, baud_rate)

    def open_device(self):
        try:
            self.device.open()
            print("XBee device opened successfully.")
        except Exception as e:
            print(f"Failed to open XBee device: {e}")

    def receive_data(self):
        try:
            print("Waiting for data...")
            while True:
                xbee_message = self.device.read_data()
                if xbee_message is not None:
                    # データをデコード
                    raw_data = xbee_message.data.decode('utf-8')
                    print(f"Received raw data: {raw_data}")

                    try:
                        data = json.loads(raw_data)
                        if isinstance(data, list):  # データがリスト形式か確認
                            return data
                        else:
                            print(f"Received data is not a list")
                    except json.JSONDecodeError:
                        print("Received data is not valid JSON.")
        except Exception as e:
            print(f"Error while receiving data: {e}")


    def close_device(self):
        if self.device is not None and self.device.is_open():
            self.device.close()
            print("XBee device closed.")

