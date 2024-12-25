import abc
from gpiozero import Servo
from time import sleep

class Iservo(abc.ABC):
     @abc.abstractmethod
     def rotate(self):
          pass

     def stop(self):
          pass
     
class Servo(Iservo):
     def __init__(self,pin):
          self.servo=Servo(pin)
     
     def rotate(self):
          #必要に応じて変える
          self.servo.value=1

     def stop(self):
          self.servo.value=0