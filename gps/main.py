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
      try:
        self.__sentence = self.__uart.readline()

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
                            # 更新されたGPSデータをログするなどの処理を後で書く
                             pass

      except Exception as e:
                print(f"GPSからの読み取りエラー: {e}")

    #経度緯度を出す
    def get_coordinates(self) -> tuple[float, float]:

       #２つの変数がnotNoneなら値を入れ、elseならNoneを入れる
        latitude = self.__gps.latitude[0] if self.__gps.latitude[0] is not None else None
        longitude = self.__gps.longitude[0] if self.__gps.longitude[0] is not None else None

        return (latitude, longitude)
    
  #gpsのデータは、役割が違う改行された複数の文で構成されているため、改行ごとにわける必要がある

   
    def delete(self):
        self.__sentence = None
        if self.__uart:
            #uartが偽の値ならエラー起こるので存在確認している
            self.__uart.close() 
        print("gpsのデータを削除しました")
