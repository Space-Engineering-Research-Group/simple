import abc
import serial
import micropyGPS
from time import sleep,time

class IGps(abc.ABC):
    @abc.abstractmethod
    def update_gps(self):
        pass

    @abc.abstractmethod
    def get_coordinate_xy(self):
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
judge = False 

class Gps(IGps):
    def __init__(self):
        self.error_counts = []
        self.error_messages = []
        self.error_log="gps Error Log"
        self.a=1
        self.ini=True

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
                error =f"Failed to open the serial port:: /dev/serial0. Ensure the port is not busy or unavailable.:--detail{e}"
                self.handle_error(error)
                                    
            except Exception as e:
            # その他のエラー（MicropyGPS の初期化エラーなど）
                if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                    self.__gps_uart.close()
                error = f"Failed to _init_ the GPS:--detail{e}"
                self.handle_error(error)
                                    #micropyGPS の設定やデータ受信に問題がある
                        
            finally:
                    self.prev_altitude = None
                    self.prev_time = None
                    if (len(self.error_messages)and self.a==0)or 5 in self.error_counts:
                        if 5 in self.error_counts:
                            if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                                self.__gps_uart.close()
                        self.log_errors()   
                        break  
            sleep(1)
        

    def update_gps(self):
        global judge
        self.error_counts = []
        self.error_messages = []
        self.error_log = "gps Error Log"
        self.a = 1
        self.ini=False


        while True:
            try:
                self.sentence = self.__gps_uart.readline()
                if self.sentence:
                    #kokode decode dekiruka tasikameru
                    while True:
                        try:
                            if self.sentence.decode('utf-8'):
                                break
                        except UnicodeDecodeError:
                            print("エラー")
                            self.sentence = self.__gps_uart.readline()
                            

                    if "$GPGGA" in self.sentence.decode('utf-8') or "$GPRMC" in self.sentence.decode('utf-8') or "$GPGLL" in self.sentence.decode('utf-8'):       
                        for x in self.sentence.decode('utf-8', errors='ignore'):
                            self.__gps.update(x)
                            self.a = 0  
                            judge = True    
                    else:
                        judge = False               
                else:
                    print("ない")
                    raise Exception("failed to get info of gps")
                
                break#消してもいいのか


            except serial.SerialException as e:
                error = f"GPS communication error:--detail{e}"
                self.handle_error(error)
            except Exception as e:
                error = f"Failed _ GPS update_gps:--detail{e}"
                self.handle_error(error)
            finally:
                if (len(self.error_messages) and self.a == 0) or 5 in self.error_counts:
                    if 5 in self.error_counts:
                            if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                                self.__gps_uart.close()
                    self.log_errors()
                    break

            sleep(1)


    def get_coordinate_xy(self):
        global judge
        self.error_counts = []
        self.error_messages = []
        self.error_log="gps Error Log"
        self.a=1
        self.ini=False

        latlist = []
        lonlist = []
  
        q=0
        
        while True:
            try:
            
                while q<30:
                    self.update_gps()
                    self.latitude = self.__gps.latitude[0]
                    self.longitude = self.__gps.longitude[0]
                    if judge == True and self.latitude != 0 and self.longitude != 0:
                        print(f"{q} Latitude: {self.__gps.latitude[0]}, Longitude: {self.__gps.longitude[0]}")
                        latlist.append(self.latitude)
                        lonlist.append(self.longitude)
                        q+=1


                ave_lat = sum(latlist) / len(latlist)
                ave_lon = sum(lonlist) / len(lonlist)
                print(f'average_latitude:{ave_lat}, average_longitude:{ave_lon}')
                self.a = 0
                print('終わった')
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
                if (len(self.error_messages)and self.a==0)or 5 in self.error_counts:
                    if 5 in self.error_counts:
                            if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                                self.__gps_uart.close()
                    self.log_errors()
                    break

            sleep(1) 


            

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
                    if (len(self.error_messages)and self.a==0)or 5 in self.error_counts:
                        if 5 in self.error_counts:
                            if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                                self.__gps_uart.close()
                        self.log_errors()
                        
                sleep(1)


    def dms_to_decimal(self):

            # 度と分に分割する
        lat_degrees = int(self.latitude / 100)  # 整数部分（度）
        lat_minutes = self.latitude % 100  # 小数部分（分）

        lon_degrees = int(self.longitude / 100)  # 整数部分（度）
        lon_minutes = self.longitude % 100  # 小数部分（分）

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
        if self.ini==False:    
            raise RuntimeError

    def handle_error(self,error):
        if str(error) not in self.error_messages:
            self.error_messages.append(str(error))
            self.error_counts.append(1)
        else:
            index = self.error_messages.index(str(error))
            self.error_counts[index] += 1
