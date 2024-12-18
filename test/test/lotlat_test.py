import serial
import micropyGPS


class Gps():
    def __init__(self):
        try:
            self.__gps_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
            self.__gps = micropyGPS.MicropyGPS(9, "dd")
        except Exception as e:
        
            if hasattr(self, '_Gps__gps_uart') and self.__gps_uart and self.__gps_uart.is_open:
                self.__gps_uart.close()  
        
        self.prev_altitude = None
        self.prev_time = None

    def update_gps(self):
        try:
            self.sentence = self.__gps_uart.readline()
            
            if self.sentence:
                for x in self.sentence.decode('ascii', errors='ignore'):
                    self.__gps.update(x)  

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
    
    def delete(self):
        self.sentence = None
        if self.__gps_uart and self.__gps_uart.is_open:
            self.__gps_uart.close()


#main   
#This is a code that measures only one point.
try:
    gps = Gps()
    i = 0
    latlist = []
    lonlist = []        

    while i <= 40:
      lat,lon = gps.get_coordinate_xy()
      if lat is None and lon is None:
          raise ValueError("lat,lon is None")
      latlist.append(lat)
      lonlist.append(lon)
      print(f"lat is {lat}\nlon is {lon}\n")
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
        print("delete is ok")

