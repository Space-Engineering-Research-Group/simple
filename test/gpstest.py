import serial
import micropyGPS
from time import sleep

class Gps:
    def __init__(self):
        self.__gps_uart = serial.Serial('/dev/serial0', 9600, timeout=10)
        self.__xbee_uart = serial.Serial('/dev/ttyUSB0', 9600, timeout=10)
        self.__gps = micropyGPS.MicropyGPS(9, "dd")
        self.__data_buffer = ""
    
    def run_gps(self):
      try:
        self.__sentence = self.__gps_uart.readline()
        if self.__sentence:
                self.__data_buffer += self.__sentence.decode('ascii', errors='ignore')
        
                while '\n' in self.__data_buffer:
                    self.__sentence, self.__data_buffer = self.__data_buffer.split('\n', 1)

                    for x in self.__sentence:
                         if 10 <= ord(x) <= 126:
                             if self.__gps.update(x):
                                 latitude = self.__gps.latitude[0]
                                 longitude = self.__gps.longitude[0]
                                 altitude = self.__gps.altitude
                                 if latitude is not None and longitude is not None and altitude is not None:
                                    self.__xbee_uart.write(f"Lat: {latitude:.6f}, Lon: {longitude:.6f}, alt: {altitude:.6f}\n".encode('utf-8'))
                                    print(f'lat is {latitude} lon is {longitude} alt is {altitude}\n')
                                    return altitude
                                 
      except serial.SerialException as e:
            print(f"GPS communication error: {e}")                               
      except Exception as e:
                print(f"GPS:error {e}")
   
    def delete(self):
        self.__sentence = None
        if self.__gps_uart:
            self.__gps_uart.close()
        if self.__xbee_uart:
            self.__xbee_uart.close()    
        print("gps of data is delete")

gps = Gps()
nowalt = 0
for i in range(6):
    alt = gps.run_gps()
    dif = alt - nowalt
    nowalt = alt
    if dif == 0:
         print('arrive')
         break
    sleep(2)
gps.delete()    





    