import abc
import serial
import micropyGPS
from time import sleep
import time


class IGps(abc.ABC):
    @abc.abstractmethod
    def update_gps(self):
        pass

    @abc.abstractmethod
    def get_coordinate_xy(self):
        pass
    
    @abc.abstractmethod
    def z_coodinate(self):
        pass
    
    @abc.abstractmethod
    def move_direction(self):
        pass
    
    @abc.abstractmethod
    def delete(self):
        pass

    @abc.abstractmethod
    def dms_to_decimal(self,lat,lon):
        pass
    
    @abc.abstractmethod
    def log_errors(self):
        pass

    @abc.abstractmethod
    def handle_error(self,error):
        pass


class Gps(IGps):
    def __init__(self):
        self.error_counts = []
        self.error_messages = []
        self.error_log="gps Error Log"
        self.a=1
        while True:
            try:
                self.__gps_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
                self.__gps = micropyGPS.MicropyGPS(9, "dd")
                self.a = 0
                break
            except serial.SerialException as e:
                # シリアルポートが開けなかった場合
                if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                    self.__gps_uart.close()
                    #ポートがビジー状態または存在しない
                    error ="Failed to open the serial port:: /dev/serial0. Ensure the port is not busy or unavailable.:--detail{e}"
                    self.handle_error(error)
                                    
            except Exception as e:
            # その他のエラー（MicropyGPS の初期化エラーなど）
                if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                    self.__gps_uart.close()
                    error = "Failed to _init_ the GPS:--detail{e}"
                    self.handle_error(error)
                                    #micropyGPS の設定やデータ受信に問題がある
                        
            finally:
                    self.prev_altitude = None
                    self.prev_time = None
                    if (len(self.error_messages)and self.a==1)or 5 in self.error_counts:
                        self.log_errors()     

            sleep(1)
        

    def update_gps(self):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "gps Error Log"
        self.a = 1
        while True:
            try:
                self.sentence = self.__gps_uart.readline()
                if self.sentence:
                    for x in self.sentence.decode('ascii', errors='ignore'):
                        self.__gps.update(x)
                        self.a = 0
                        break

            except serial.SerialException as e:
                error = f"GPS communication error:--detail{e}"
                self.handle_error(error)
            except Exception as e:
                error = f"Failed _ GPS update_gps:--detail{e}"
                self.handle_error(error)
            finally:
                if (len(self.error_messages) and self.a == 1) or 5 in self.error_counts:
                    self.log_errors()

            sleep(1)


    def get_coordinate_xy(self):
        self.error_counts = []
        self.error_messages = []
        self.error_log="gps Error Log"
        self.a=1
        while True:
            try:
                lali = [] #latitude_list
                loli = [] #longitude_list
                for i in range(30):
                    start_time = time.time()

                    self.update_gps()
                    latitude = self.__gps.latitude[0]
                    longitude = self.__gps.longitude[0]
                    if latitude is None and longitude is None:      
                        raise ValueError( "lat , lon is None")
                        
                    while True:
                        current_time = time.time()
                    
                        time_difference = current_time - start_time

                        if time_difference > 0.11:
                            m_latitude, m_longitude = self.dms_to_decimal(latitude,longitude)
                            if m_latitude is None and m_longitude is None:
                                raise ValueError("m_lat , m_lon is None")
            
                            lali.append(m_latitude)
                            loli.append(m_longitude)
                            break

                ave_lat = sum(lali)/len(lali)
                ave_lon = sum(loli)/len(loli)
                self.a=0               
                return ave_lat, ave_lon
                

            except ValueError as e:
                error = f"Failed _ GPS get_coordinate_xy:--detail{e}"
                self.handle_error(error)
            except serial.SerialException as e:
                error = "GPS communication error: --detail{e}"
                self.handle_error(error)
            except Exception as e:
                error =f"Failed _ GPS xy_coordinates:--detail{e}"
                self.handle_error(error)
            finally:
                if (len(self.error_messages)and self.a==1)or 5 in self.error_counts:
                    self.log_errors()

            sleep(1)      


    def z_coordinate(self): 
        self.error_counts=[]
        self.error_messages=[]
        self.error_log="gps Error Log"
        self.a=1
        while True:
            try:
                alt_list = []
                while True:
                    self.update_gps()
                    start_time = time.time()
                    #1秒間に3回取得する
                    for 3 in range(3):
                        alt = self.__gps.altitude[0] #単位はmである
                        if alt is None:
                            raise ValueError("alt is None")
                        alt_list.append(alt)
                        sleep(0.2)
                        while True:
                            #1秒経過するまで待つ
                            current_time = time.time()
                            time_difference = current_time - start_time
                            if time_difference > 1:
                                ave_alt = sum(alt_list)/len(alt_list)
                                self.a=0
                                return ave_alt
                            
            except ValueError as e:
                error = f"Failed _ GPS z_coordinate:--detail{e}"
                self.handle_error(error)        
            except serial.SerialException as e:
                error = f"GPS communication error:--detail{e}"
                self.handle_error(error)
            except Exception as e:
                error = f"Failed _ GPS z_coordinate:--detail{e}"
                self.handle_error(error)
            finally:
                if (len(self.error_messages)and self.a==1)or 5 in self.error_counts:
                    self.log_errors()
                        
            sleep(1)
    
    

    def move_direction(self):
         #誤差あれば、30回取得するコードにする
        self.error_counts=[]
        self.error_messages=[]
        self.error_log="gps Error Log"
        self.a=1
        while True:
            try:
                direction = [] 
                for i in range(30):
                    start_time = time.time()
                    self.update_gps()

                    move_direction = self.__gps.course
                    if move_direction is None:
                        raise AttributeError("move_direction is None")
                    while True:
                        current_time = time.time()
                        time_difference = current_time - start_time
                        if time_difference > 0.11:
                            direction.append(move_direction)
                            break
                ave_direction = sum(direction)/len(direction)
                self.a=0
                return ave_direction
            except AttributeError as e:
                               #move_direction = None,undefined のとき
                error = f"Failed to get GPS course.:--detail{e}" 
                self.handle_error(error)
            except Exception as e:
                error = f"Failed _ GPS course.:--detail{e}" 
                self.handle_error(error)
            finally:
                if (len(self.error_messages)and self.a==1)or 5 in self.error_counts:
                    self.log_errors()
                        
            sleep(1)    

            import math
#self.__gps.courseの中身
# def calculate_bearing(lat1, lon1, lat2, lon2):
#     # 緯度・経度をラジアンに変換
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     d_lon = lon2 - lon1

#     # ベアリング計算
#     x = math.sin(d_lon) * math.cos(lat2)
#     y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
#     bearing = math.atan2(x, y)

#     # 度単位に変換し、0～360度に正規化
#     return (math.degrees(bearing) + 360) % 360

    
    def delete(self):
        self.error_counts=[]
        self.error_messages=[]
        self.error_log="gps Error Log"
        self.a=1
        while True:
            self.sentence = None
        
            if self.__gps_uart:
                try:
                    if self.__gps_uart.is_open:
                        self.__gps_uart.close()
                        self.a=0
                        break           
                except serial.SerialException as e:
                    error = "Failed to close the serial port.:--detail{e}" 
                    self.handle_error(error)
                finally:
                    if (len(self.error_messages)and self.a==1)or 5 in self.error_counts:
                        self.log_errors()
                        
                sleep(1)


    def dms_to_decimal(self,lat,lon):

            # 度と分に分割する
        lat_degrees = int(lat / 100)  # 整数部分（度）
        lat_minutes = lat % 100  # 小数部分（分）

        lon_degrees = int(lon / 100)  # 整数部分（度）
        lon_minutes = lon % 100  # 小数部分（分）

        # 10進法に変換
        m_latitude = lat_degrees + lat_minutes / 60
        m_longitude = lon_degrees + lon_minutes / 60

        return m_latitude, m_longitude
    
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
            self.error_log=f"cds:Error--{list[index]} other errors--{result}"
            raise RuntimeError

    def handle_error(self,error):
        if str(error) not in self.error_messages:
            self.error_messages.append(str(error))
            self.error_counts.append(1)
        else:
            index = self.error_messages.index(str(error))
            self.error_counts[index] += 1


    