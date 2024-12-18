from gpiozero import PWMOutputDevice,DigitalOutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory
from abc import ABC,abstractmethod

factory = PiGPIOFactory()

class Imotor(ABC):
    @abstractmethod
    def forward(self):
        pass

    
    @abstractmethod
    def turn_right(self):
        pass
    
    @abstractmethod
    def turn_left(self):
        pass

    @abstractmethod
    def release(self):
        pass
    
    
class Motor(Imotor):
    def __init__(self,rdir_1,rdir_2,rPWM,ldir_1,ldir_2,lPWM):
        self.right_in1=DigitalOutputDevice(rdir_1,pin_factory=factory)
        self.right_in2=DigitalOutputDevice(rdir_2,pin_factory=factory)
        self.right_PWM=PWMOutputDevice(rPWM,pin_factory=factory)
        
        self.left_in1=DigitalOutputDevice(ldir_1,pin_factory=factory)
        self.left_in2=DigitalOutputDevice(ldir_2,pin_factory=factory)
        self.left_PWM=PWMOutputDevice(lPWM,pin_factory=factory)

        self.right_PWM.value=204/255
        self.left_PWM.value=204/255
        
    def forward(self):
        self.right_in1.on()
        self.right_in2.off()

        self.left_in1.off()
        self.left_in2.on()

    def turn_right(self):
        self.right_in1.off()
        self.right_in2.on()

        self.left_in1.off()
        self.left_in2.on()

    def turn_left(self):
        self.right_in1.on()
        self.right_in2.off()

        self.left_in1.on()
        self.left_in2.off()

    #main.pyファイルを書き直しておく
    def release(self):
        self.right_in1.off()
        self.right_in2.off()

        self.left_in1.off()
        self.left_in2.off()



        
    
