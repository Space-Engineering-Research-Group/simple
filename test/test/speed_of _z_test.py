import serial
import micropyGPS

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

    def z_coordinate(self):
        try:
            self.update_gps()
        except:
            print("gps comminucation error")    
        alt = self.__gps.altitude[0]
        return alt 

    def delete(self):
        self.sentence = None
        if self.__gps_uart and self.__gps_uart.is_open:
            self.__gps_uart.close()
        if self.__xbee_uart and self.__xbee_uart.is_open:
            self.__xbee_uart.close()

try:
    gps = Gps()
    i = 0

    while i <= 20:
        zc = gps.z_coordinate()
        if zc is None:
            raise ValueError("sz is None")        

except ValueError as ve:
    print(f"ValueError: {ve}")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()  

finally:
    if 'gps' in locals():
        gps.delete()

            
