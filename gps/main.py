import abc
import serial
import micropyGPS
import math
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


class Gps(IGps):
    def __init__(self):
        self.error_counts = []
        self.error_messages = []
        self.error_log="cds Error Log"
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
                    error ="Failed to open the serial port:: /dev/serial0. Ensure the port is not busy or unavailable."
                    self.handle_error(error)
                                    
            except Exception as e:
            # その他のエラー（MicropyGPS の初期化エラーなど）
                if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                    self.__gps_uart.close()
                    error = "Failed to _init_ the GPS"
                    self.handle_error(error)
                                    #micropyGPS の設定やデータ受信に問題がある
                        
            finally:
                    if (len(self.error_messages)and self.a==1)or 5 in self.error_counts:
                        self.log_errors()                            
    
        self.prev_altitude = None
        self.prev_time = None

    
    def update_gps(self):
        try:
            self.sentence = self.__gps_uart.readline()
            
            if self.sentence:
                for x in self.sentence.decode('ascii', errors='ignore'):
                    self.__gps.update(x)  

        except serial.SerialException as e:
            raise RuntimeError("GPS communication error")from e
        except Exception as e:
            raise RuntimeError(f"Failed _ GPS update_gps: {str(e)}")
        

    def get_coordinate_xy(self):
        try:
            lali = [] #latitude_list
            loli = [] #longitude_list
            for i in range(30):
                start_time = time.time()
                while True:
                    self.update_gps()

                    latitude = self.__gps.latitude[0]
                    longitude = self.__gps.longitude[0]
                    if latitude is None and longitude is None:      
                        raise ValueError(f"lat , lon is None ")
                    current_time = time.time()
                    
                    time_difference = current_time - start_time

                    if time_difference > 0.11:
                        m_latitude, m_longitude = self.dms_to_decimal(latitude,longitude)
                        if m_latitude is None and m_longitude is None:
                            raise ValueError(f"m_lat , m_lon is None")
            
                        lali.append(m_latitude)
                        loli.append(m_longitude)
                        break

            ave_lat = sum(lali)/len(lali)
            ave_lon = sum(loli)/len(loli)               
            return ave_lat, ave_lon

        except ValueError as e:
            raise RuntimeError(f"Failed _ GPS get_coordinate_xy: {str(e)}")
        except serial.SerialException as e:
            raise RuntimeError("GPS communication error")
        except Exception as e:
            raise RuntimeError(f"Failed _ GPS xy_coordinates: {str(e)}")
        

    def z_coordinate(self,grand_z): #grand_zは全体のmainコードで定義
        try:
            while True:
                start_time = time.time()
                while True:
                    self.update_gps()

                    alt = self.__gps.altitude[0] #単位はmである
                    if alt is None:
                        raise ValueError("alt is None")
                    current_time = time.time()

                    time_difference = time.time() - start_time

                    if time_difference > 1:
                        break

                z_difference = grand_z - alt
                if z_difference <= 2:
                    return True
                    break      
            
        
        except serial.SerialException as e:
            raise RuntimeError("GPS communication error")
        except Exception as e:
            raise RuntimeError(f"Failed _ GPS z_coordinate: {str(e)}")
    

    def move_direction(self):
        try:
            move_direction = self.__gps.course
            return move_direction
        except AttributeError as e:
                               #move_direction = None,undefined のとき
            raise RuntimeError("Failed to get GPS course.") 
        except Exception as e:
            raise RuntimeError("Failed _ GPS course.") 
    
    def delete(self):
        self.sentence = None
        
        if self.__gps_uart:
            try:
                if self.__gps_uart.is_open:
                    self.__gps_uart.close()
            except serial.SerialException as e:
                raise RuntimeError("Failed to close the serial port.") 

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
