from gpiozero import MCP3008
from abc import ABC,abstractmethod

class Icds(ABC):
    @abstractmethod
    def get_brightness(self):
        pass

class Cds(Icds):
    def __init__(self):
        self.cds=MCP3008(channel=0)
    
    def get_brightness(self):
        brightness=self.cds.value
        return brightness