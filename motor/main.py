from gpiozero import Motor
import abc

class Imotor(abc.ABC):
    @abc.abstractmethod
    def forward(self):
        raise NotImplementedError() 
    
    @abc.abstractmethod
    def backward(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def turn_right(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def turn_left(self):
        raise NotImplementedError()
    
class Motor(Imotor):
    def __init__(self, forward_left_pin, back_left_pin, forward_right_pin, back_right_pin):
        
        self.left_motor = Motor(forward_left_pin, back_left_pin)
        self.right_motor = Motor(forward_right_pin, back_right_pin)
        

    def forward(self):
        self.left_motor.forward()
        self.right_motor.forward()
    
    def backward(self):
        self.left_motor.backward()
        self.right_motor.backward()

    def turn_right(self):
        self.left_motor.forward()
        self.right_motor.backward()  

    def turn_left(self):
        self.left_motor.backward()
        self.right_motor.forward()
       
    
    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()

        
    
