import abc
import serial
import micropyGPS

class IGps(abc.ABC):
    @abc.abstractmethod
    def run_gps(self):
        
        raise NotImplementedError()

    @abc.abstractmethod
    def get_coordinates(self) -> tuple[float, float]:
       
        raise NotImplementedError()

class Gps(IGps):
    def __init__(self):
        #ここのポートと通信速度、タイムアウトの値は仮に設定した
        self.__uart = serial.Serial('/dev/serial0', 9600, timeout=10)
        self.__gps = micropyGPS.MicropyGPS(9, "dd")
        self.__data_buffer = ""

    def run_gps(self):
      
        while True:
            try:
                sentence = self.__uart.readline()
                
                if sentence:
                    self.__data_buffer += sentence.decode('ascii', errors='ignore')
                   
                    while '\n' in self.__data_buffer:
                        sentence, self.__data_buffer = self.__data_buffer.split('\n', 1)

                        for x in sentence:
                            if 10 <= ord(x) <= 126:
                                if self.__gps.update(x):
                                    # 更新されたGPSデータをログするなどの処理を後で書く
                                    pass

            except Exception as e:
                print(f"GPSからの読み取りエラー: {e}")

    def get_coordinates(self) -> tuple[float, float]:

       #２つの変数がnotNoneなら値を入れ、elseならNoneを入れる
        latitude = self.__gps.latitude[0] if self.__gps.latitude[0] is not None else None
        longitude = self.__gps.longitude[0] if self.__gps.longitude[0] is not None else None

        return latitude, longitude