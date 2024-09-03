import abc
from gpiozero from Servo

class Iservo(abc.ABC):
     @abc.abstractmethod
     def rotate(self):
          pass
     
class Servo(Iservo):
     def __init__(self,pin):
          #maxpulseとminpulseも必要があれば指定
          self.servo=Servo(pin)
     
     def rotate(self):
          #必要に応じて変える
          self.servo.max()