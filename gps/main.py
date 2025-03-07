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
    def log_errors(self):
        pass

    @abc.abstractmethod
    def handle_error(self,error):
        pass
gpsjudge = False 

class Gps(IGps):
    def __init__(self):
        self.error_counts = []
        self.error_messages = []
        self.error_log="gps Error Log"
        self.a=1
        self.ini=True

        p=0

        while True:
            p+=1
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
        global gpsjudge
        self.error_counts = []
        self.error_messages = []
        self.error_log = "gps Error Log"
        self.a = 1
        self.ini=False
        p=0
        while True:
            p+=1
            try:
                kako = time()
                self.sentence = self.__gps_uart.readline()

                if self.sentence:

                    while True:
                        try:
                            if self.sentence.decode('utf-8'):
                                break#ここめっちゃ大事
                        except UnicodeDecodeError:
                            self.sentence = self.__gps_uart.readline()

                    if "$GPGGA" in self.sentence.decode('utf-8') or "$GPRMC" in self.sentence.decode('utf-8') or "$GPGLL" in self.sentence.decode('utf-8'):  
                        for x in self.sentence.decode('utf-8', errors='ignore'):
                            self.__gps.update(x)
                            self.a = 0  
                            gpsjudge = True      
                    break#これも大事                   

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

            while True:        
                ima = time()
                if ima - kako > 0.1:
                    break


    def get_coordinate_xy(self):
        global gpsjudge
        self.error_counts = []
        self.error_messages = []
        self.error_log="gps Error Log"
        self.a=1
        self.ini=False

        latlist = []
        lonlist = []
  
        q=0
        p=0
        while True:
            while q<31:
                print(p)
                while True:
                    try:
                        self.update_gps()
                        break
                    except Exception as e:
                        if gpsjudge == False:
                            self.update_gps()                 
                while True:
                    try:
                        self.latitude = self.__gps.latitude[0]
                        self.longitude = self.__gps.longitude[0]
                        self.a = 0   
                        break
                    except Exception as e:
                        error = f"Failed to get latitude and longitude:--detail{e}"
                        self.handle_error(error)
                    finally:
                        if (len(self.error_messages)and self.a==0)or 5 in self.error_counts:
                            if 5 in self.error_counts:
                                if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                                    self.__gps_uart.close()    
                            self.log_errors()
                            break            
                print(self.latitude,self.longitude)
                if gpsjudge == True and self.latitude != 0 and self.longitude != 0:
                    latlist.append(self.latitude)
                    lonlist.append(self.longitude)
                    q+=1
     
            ave_lat = sum(latlist) / len(latlist)
            ave_lon = sum(lonlist) / len(lonlist)
            print(f'average_latitude:{ave_lat}, average_longitude:{ave_lon}')
            self.a = 0
            return ave_lat, ave_lon
 
    def get_xy_ceak(self):
        global gpsjudge
        self.error_counts = []
        self.error_messages = []
        self.error_log="gps Error Log"
        self.a=1
        self.ini=False
        p=0
        while True:
                while True:
                    try:
                        self.update_gps()
                        break
                    except Exception as e:
                        if gpsjudge == False:
                            self.update_gps()
                   
                while True:
                    p+=1
                    try:
                        latitude = self.__gps.latitude[0]
                        longitude = self.__gps.longitude[0]
                        if gpsjudge == True and latitude != 0 and longitude != 0:
                            self.a = 0    
                            return latitude,longitude
                    except Exception as e:
                        error = f"Failed to get latitude and longitude:--detail{e}"
                        self.handle_error(error)
                    finally:
                        if (len(self.error_messages)and self.a==0)or 5 in self.error_counts:
                            if 5 in self.error_counts:
                                if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                                    self.__gps_uart.close()    
                            self.log_errors()
                            break    

    def delete(self):
        self.error_counts=[]
        self.error_messages=[]
        self.error_log="gps Error Log"
        self.a=1
        self.ini=False
        while True:
            self.sentence = None
        
            if self.__gps_uart:
                try:
                    kako = time()
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
                while True:        
                    ima = time()
                    if ima - kako > 0.1:
                        break        
                        
    
    def log_errors(self):
        error_list = []
        for count, message in zip(self.error_counts, self.error_messages):
            error_list.append(f"{count}*{message}")
        if self.a == 0:
            self.error_log = "gps:Error--"+",".join(error_list)
        elif 5 in self.error_counts:
            if len(error_list) == 1:
                self.error_log=f"gps:Error--{error_list[0]}"
            else:
                index = self.error_counts.index(5)
                result = error_list[:index] + error_list[index + 1:]
                result = ",".join(result)
                self.error_log = f"gps:Error--{error_list[index]} other errors--{result}"
            if self.ini==False:
                raise RuntimeError


    def handle_error(self,error):
        if str(error) not in self.error_messages:
            self.error_messages.append(str(error))
            self.error_counts.append(1)
        else:
            index = self.error_messages.index(str(error))
            self.error_counts[index] += 1