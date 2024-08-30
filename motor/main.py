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
    
class motor(Imotor):
    def __init__(self, foward_left_pin, back_left_pin, foward_right_pin, back_right_pin):
        try:
            self.left_motor = Motor(foward_left_pin, back_left_pin)
            self.right_motor = Motor(foward_right_pin, back_right_pin)
        except Exception as e:
            print(f"モーターの初期化中にエラー発生:{e}")
            raise     

    def foward(self):
        self.left_motor.foward()
        self.right_motor.foward()
    
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
    
