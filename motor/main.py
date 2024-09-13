from gpiozero import OutputDevise
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
    
    #高井君のスレッドみろ
class Motor(Imotor):
    def __init__(self, dir1_1, dir1_2, dir2_1, dir2_2):
        
       self._dir11 = OutputDevise(dir1_1)
       self._dir12 = OutputDevise(dir1_2)
       self._dir21 = OutputDevise(dir2_1)
       self._dir22 = OutputDevise(dir2_2)

    def forword(self):
        self._dir11.on()
        self._dir12.off()
        #逆になるにで、反対になる
        self._dir21.off()
        self._dir22.on()

    def backword(self):
        self._dir11.off()
        self._dir12.on()
        #逆になるにで、反対になる
        self._dir21.on()
        self._dir22.off()

    def stop(self):
        self._dir11.off()
        self._dir12.off()
        self._dir21.off()
        self._dir22.off()




        
    
