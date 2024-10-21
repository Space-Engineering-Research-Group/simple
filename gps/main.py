import abc
import serial
import micropyGPS

class IGps(abc.ABC):
    @abc.abstractmethod
    def run_gps(self):
        pass
    @abc.abstractmethod
    def get_coordinates(self) -> tuple[float, float]:
       pass

class Gps(IGps):
    def __init__(self):
        pass
    def get_coordinate_xy(self):
        self.latitude=0
        self.longitude=0
        return self.latitude,self.longitude
   
    def get_speed_z(self):
        self.speed=0
        return self.speed
    
    def move_direction(self):
        direction=0
        return direction
    
    def delete(self):
        pass

    