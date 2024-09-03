import abc
from GPIOZERO from servo

class Iservo(abc.ABC):
     @abc.abstractmethod
     def rotate(self):
          pass
     
class Servo(Iservo):
     def __init__(self):
               self._servo = servo 