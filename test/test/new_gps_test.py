import serial
import micropyGPS
import time


class Gps():
    def __init__(self):
        try:
            self.__gps_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
            self.__xbee_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
            self.__gps = micropyGPS.MicropyGPS(9, "dd")
        except Exception as e:
        
            if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                self.__gps_uart.close()
            if hasattr(self, '_Gps__xbee_uart') and self.__xbee_uart and self.__xbee_uart.is_open:
                self.__xbee_uart.close()
            raise e  
        
        self.prev_altitude = None
        self.prev_time = None

    def update_gps(self):
        try:
            self.sentence = self.__gps_uart.readline()
            
            if self.sentence:
                for x in self.sentence.decode('ascii', errors='ignore'):
                    self.gps.update(x)  

        except serial.SerialException as e:
            print(f"GPS communication error: {e}")  
        except Exception as e:
            print(f"GPS communication error: {e}")  



    def get_coordinate_xy(self):
        try:
            self.update_gps()
            latitude = self.__gps.latitude[0]
            longitude = self.__gps.longitude[0]
            if latitude is not None and longitude is not None:
            
                return latitude, longitude

        except serial.SerialException as e:
            print(f"GPS communication error: {e}")
        except Exception as e:
            print(f"GPS error: {e}")
        
        return None, None

    def get_speed_z(self):
        try:
            self.update_gps()
        except Exception as e:
            print(f"Error updating GPS: {e}")

            altitude = self.__gps.altitude[0] i
            if altitude is None:
                raise ValueError("altitude is None.")
            current_time = time.time()

            if altitude is not None:                    
                if self.prev_altitude is not None and self.prev_time is not None:
                    raise ValueError("self.prev_altitude is None and self.prev_time is None.")
                        
                time_diff = current_time - self.prev_time
                if time_diff > 0:
                    speed_z = (altitude - self.prev_altitude) / time_diff
                            
                    self.prev_altitude = altitude
                    self.prev_time = current_time
                    return speed_z
                else:
                    
                    self.prev_altitude = altitude
                    self.prev_time = current_time
                                
        except serial.SerialException as e:
            print(f"GPS communication error: {e}")
        except Exception as e:
            print(f"GPS error: {e}")
        
        return None
    
    def move_direction(self):
        move_direction = self.__gps.course
        return move_direction
    
    def delete(self):
        self.sentence = None
        if self.__gps_uart and self.__gps_uart.is_open:
            self.__gps_uart.close()
        if self.__xbee_uart and self.__xbee_uart.is_open:
            self.__xbee_uart.close()    
#main   
#This is a code that measures only one point.
import time
try:
    gps = Gps()
    i = 0
    latlist = []
    lonlist = []
    sz_list = []
    md_list = []

    while i <= 10:
        sz = gps.get_speed_z()
        if sz is None:
            raise ValueError("sz is None")   
        sz_list.append(sz)
        time.sleep(1)        
    
    print("under,speed_of_z\n")  
    if sz_list is None:
         raise ValueError("speed_of_z_list is None")
    for s in sz_list:
        print(s)          

    while i <= 10:
        md = gps.move_direction()
        if md is None:
            raise ValueError("sz is None")   
        md_list.append(md)
        time.sleep(1)        
    
    print("under,speed_of_z\n")  
    if md_list is None:
         raise ValueError("speed_of_z_list is None")
    for m in md_list:
        print(m)
    
    while i <= 40:
      lat,lon = gps.get_coordinate_xy()
      if lat is None and lon is None:
          raise ValueError("lat,lon is None")
      latlist.append(lat)
      lonlist.append(lon)
      print(f'Latitude: {lat}, Longitude: {lon}\n')
      time.sleep(1)
      i = i + 1

    print("under,all_lat(ido)\n")  
    if latlist is None:
         raise ValueError("latlist is None")
    for la in latlist:
        print(la)
    
    print("under,all_lon(keio)\n")
    if lonlist is None:
         raise ValueError("lonlist is None")
    for lo in lonlist:
        print(lo)    

except ValueError as ve:
    print(f"ValueError: {ve}")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()  

finally:
    if 'gps' in locals():
        gps.delete()
