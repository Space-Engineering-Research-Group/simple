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
                    self.__gps.update(x)  

        except serial.SerialException as e:
            print(f"GPS communication error: {e}")  
        except Exception as e:
            print(f"GPS communication error: {e}")  

    def move_direction(self):
        move_direction = self.__gps.course
        return move_direction

    def delete(self):
        self.sentence = None
        if self.__gps_uart and self.__gps_uart.is_open:
            self.__gps_uart.close()
        if self.__xbee_uart and self.__xbee_uart.is_open:
            self.__xbee_uart.close() 

import time

try:
    gps = Gps()
    i = 0
    md_list = []

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

except ValueError as ve:
    print(f"ValueError: {ve}")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()  

finally:
    if 'gps' in locals():
        gps.delete()

            
                