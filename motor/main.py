from gpiozero import PWMOutputDevice,DigitalOutputDevice
from abc import ABC,abstractmethod

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
    def __init__(self,rdir_1,rdir_2,rPWM,ldir_1,ldir_2,lPWM,factory):
        self.error_counts=[]   
        self.error_messages=[]
        self.error_log="motor:Error"
        self.a=1
        while True:
            try:
                self.right_in1=DigitalOutputDevice(rdir_1,pin_factory=factory)
                self.right_in2=DigitalOutputDevice(rdir_2,pin_factory=factory)
                self.right_PWM=PWMOutputDevice(rPWM,pin_factory=factory)
                self.a=0
                break
            except GPIOPinInUse as e:
                error=f"right--motor:Error initializing right motor--detail{e}"
                self.handle_error(error)
            except Exception as e:
                error=f"right--motor:Unexpected error during initialization--detail{e}"
                self.handle_error(error)
            
        
            self.left_in1=DigitalOutputDevice(ldir_1,pin_factory=factory)
            self.left_in2=DigitalOutputDevice(ldir_2,pin_factory=factory)
            self.left_PWM=PWMOutputDevice(lPWM,pin_factory=factory)

            self.right_PWM.value=1
            self.left_PWM.value=1
        
    def forward(self,speed=1):
        self.right_PWM.value=speed
        self.left_PWM.value=speed

        self.right_in1.on()
        self.right_in2.off()

        self.left_in1.off()
        self.left_in2.on()

    def turn_right(self,speed=1):
        self.right_PWM.value=speed
        self.left_PWM.value=speed

        self.right_in1.off()
        self.right_in2.on()

        self.left_in1.off()
        self.left_in2.on()

    def turn_left(self,speed=1):
        self.right_PWM.value=speed
        self.left_PWM.value=speed

        self.right_in1.on()
        self.right_in2.off()

        self.left_in1.on()
        self.left_in2.off()
    
    def stop(self):
        self.right_PWM.value=0
        self.left_PWM.value=0

    #main.pyファイルを書き直しておく
    def release(self):
        self.right_in1.off()
        self.right_in2.off()

        self.left_in1.off()
        self.left_in2.off()

    def handle_error(self,error):
        if str(error) not in self.error_messages:
            self.error_messages.append(str(error))
            self.error_counts.append(1)
        else:
            index = self.error_messages.index(str(error))
            self.error_counts[index] += 1


    def log_errors(self):
        list=[]
        for count,message in zip(self.error_counts,self.error_messages):
            list.append(f"{count}*{message}")
        if self.a==0:
            self.error_log=",".join(list)
        elif 5 in self.error_counts:
            if len(list) == 1:
                self.error_log=f"cds:Error--{list[0]}"
            else:
                index=self.error_counts.index(5)
                result=list[:index]+list[index+1:]
                result=",".join(result)
                self.error_log=f"cds:Error--{list[index]} other errors--{result}"
            raise RuntimeError

        
    
