import abc
import serial
import micropyGPS

class IGps(abc.ABC):
    @abc.abstractmethod
    def run_gps(self):
        pass
    @abc.abstractmethod
    def get_coordinates(self) -> tuple[float, float]:
       pass

class Gps(IGps):
    def __init__(self):
        #ここのポートと通信速度、タイムアウトの値は仮に設定した
        self.__gps_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
        self.__xbee_uart = serial.Serial('/dev/ttyUSB0', 9600, timeout=10)
        self.__gps = micropyGPS.MicropyGPS(9, "dd")
        self.__data_buffer = ""

    def run_gps(self):
      try:
        self.__sentence = self.__gps_uart.readline()

        #バッファにgpsのデータASCIIにしてを蓄積
        if self.__sentence:
                self.__data_buffer += self.__sentence.decode('ascii', errors='ignore')
        
                #改行ごとに分けて、一番最初のデータをsentenceに格納
                while '\n' in self.__data_buffer:
                    self.__sentence, self.__data_buffer = self.__data_buffer.split('\n', 1)

                    #一文字ずつ分析していき、アップデートする
                    for x in self.__sentence:
                         if 10 <= ord(x) <= 126:
                             if self.__gps.update(x):
                                 latitude = self.__gps.latitude[0]
                                 longitude = self.__gps.longitude[0]
                                 if latitude is not None and longitude is not None:
                                     #もう一つのxbeeに送る
                                     self.__xbee_uart.write(f"Lat: {latitude:.6f}, Lon: {longitude:.6f}\n".encode('utf-8'))
      except serial.SerialException as e:
            print(f"GPS communication error: {e}")                               
      except Exception as e:
                print(f"GPS:error {e}")
    
  #gpsのデータは、役割が違う改行された複数の文で構成されているため、改行ごとにわける必要がある
   #受信側のコードは別にある
   
    def delete(self):
        self.__sentence = None
        if self.__gps_uart:
            self.__gps_uart.close()
        if self.__xbee_uart:
            self.__xbee_uart.close()    

        print("gps of data is delete")

    