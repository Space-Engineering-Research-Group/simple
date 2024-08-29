from abc import ABC,abstractmethod

import serial
import micropyGPS

class IGps(ABC):
    @abstractmethod
    def run_gps(self):
        pass

    @abstractmedhod
    def get_coordinates(self) ->(float,float): # type: ignore
        pass


class Gps(IGps):
    def __init__(self):
        self.ser=serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
    
    def get_coordinates(self) ->(float,float): #type:ignore
        self.deta=self.ser.readline()