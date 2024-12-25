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
        self.right_error_counts=[]
        self.right_error_messages=[]
        self.right_error_log="right motor log"
        self.a=1
        while True:
            try:
                self.right_PWM.value=1
                self.right_in1=DigitalOutputDevice(rdir_1,pin_factory=factory)
                self.right_in2=DigitalOutputDevice(rdir_2,pin_factory=factory)
                self.right_PWM=PWMOutputDevice(rPWM,pin_factory=factory)
                self.a=0
                break
            except Exception as e:
                error=f"right motor initialization failed: {e}"
                self.right_handle_error(error)
            finally:
                if (len(self.right_error_counts) and self.a==0)or 5 in self.right_error_counts:
                    self.right_log_errors()
                    break

        self.left_error_counts=[]
        self.left_error_messages=[]
        self.left_error_log="right motor log"
        self.a=1
        
        while True:
            try:
                self.left_PWM.value=1
                self.left_in1=DigitalOutputDevice(ldir_1,pin_factory=factory)
                self.left_in2=DigitalOutputDevice(ldir_2,pin_factory=factory)
                self.left_PWM=PWMOutputDevice(lPWM,pin_factory=factory)
                self.a=0
                break
            except Exception as e:
                error=f"left motor initialization failed--detail{e}"
                self.left_handle_error(error)

            finally:
                if (len(self.right_error_counts)and self.a==0)or 5 in self.left_error_counts:
                    self.left_log_errors()
                    break
        
        self.judge_error()

        
        
    def forward(self, speed):
        self.right_error_counts=[]
        self.right_error_messages=[]
        self.right_error_log="right motor log"
        self.a=1
        
        while True:
            try:
                self.right_PWM.value = speed
                self.right_in1.on()
                self.right_in2.off()
                self.a=0
                break
            except Exception as e:
                error = f"right motor error during forward motion--detail {e}"
                self.right_handle_error(error)
            finally:
                if (len(self.right_error_counts) and self.a==0)or 5 in self.right_error_counts:
                    self.right_log_errors()
                    break

        self.left_error_counts=[]
        self.left_error_messages=[]
        self.left_error_log="right motor log"
        self.a=1

        while True:
            try:
                self.left_PWM.value = speed
                self.left_in1.off()
                self.left_in2.on()
                self.a=0
                break
            except Exception as e:
                error = f"left motor error during forward motion--detail {e}"
                self.left_handle_error(error)
            finally:
                if (len(self.right_error_counts)and self.a==0)or 5 in self.left_error_counts:
                    self.left_log_errors()
                    break

        self.judge_error()


    def backward(self, speed):
        self.right_error_counts=[]
        self.right_error_messages=[]
        self.right_error_log="right motor log"
        self.a=1

        while True:
            try:
                self.right_PWM.value = speed
                self.right_in1.off()
                self.right_in2.on()
                self.a=0
                break
            except Exception as e:
                error = f"right motor error during backward motion--detail {e}"
                self.right_handle_error(error)
            finally:
                    if (len(self.right_error_counts) and self.a==0)or 5 in self.right_error_counts:
                        self.right_log_errors()
                        break

        self.left_error_counts=[]
        self.left_error_messages=[]
        self.left_error_log="right motor log"
        self.a=1

        while True:
            try:
                self.left_PWM.value = speed
                self.left_in1.on()
                self.left_in2.off()
                self.a=0
                break
            except Exception as e:
                error = f"left motor error during backward motion--detail {e}"
                self.left_handle_error(error)
            finally:
                if (len(self.right_error_counts)and self.a==0)or 5 in self.left_error_counts:
                    self.left_log_errors()
                    break
            
        self.judge_error()


    def turn_right(self, speed):
        self.right_error_counts=[]
        self.right_error_messages=[]
        self.right_error_log="right motor log"
        self.a=1
        while True:
            try:
                self.right_PWM.value = speed
                self.right_in1.off()
                self.right_in2.on()
                self.a=0
                break
            except Exception as e:
                error = f"right motor error during right turn--detail {e}"
                self.right_handle_error(error)
            finally:
                    if (len(self.right_error_counts) and self.a==0)or 5 in self.right_error_counts:
                        self.right_log_errors()
                        break

        self.left_error_counts=[]
        self.left_error_messages=[]
        self.left_error_log="right motor log"
        self.a=1

        while True:
            try:
                self.left_PWM.value = speed
                self.left_in1.off()
                self.left_in2.on()
            except Exception as e:
                error = f"left motor error during right turn--detail {e}"
                self.left_handle_error(error)
            finally:
                if (len(self.right_error_counts)and self.a==0) or 5 in self.right_error_counts:
                    self.right_log_errors()
                    break
        
        self.judge_error()

    def turn_left(self, speed):
        self.right_error_counts=[]
        self.right_error_messages=[]
        self.right_error_log="right motor log"
        self.a=1

        while True:
            try:
                self.right_PWM.value = speed
                self.right_in1.on()
                self.right_in2.off()
                self.a=0
                break
            except Exception as e:
                error = f"right motor error during left turn--detail {e}"
                self.right_handle_error(error)
            finally:
                    if (len(self.right_error_counts) and self.a==0)or 5 in self.right_error_counts:
                        self.right_log_errors()
                        break

        self.left_error_counts=[]
        self.left_error_messages=[]
        self.left_error_log="right motor log"
        self.a=1

        while True:
            try:
                self.left_PWM.value = speed
                self.left_in1.on()
                self.left_in2.off()
                self.a=0
                break
            except Exception as e:
                error = f"left motor error during left turn--detail {e}"
                self.left_handle_error(error)
            finally:
                if (len(self.right_error_counts)and self.a==0)or 5 in self.left_error_counts:
                    self.left_log_errors()
                    break

        self.judge_error()

    
    def stop(self):
        self.right_error_counts = []
        self.right_error_messages = []
        self.right_error_log = "right motor log"
        self.a = 1

        while True:
            try:
                self.right_PWM.value = 0
                self.right_in1.on()
                self.right_in2.on()
                self.a = 0
                break
            except Exception as e:
                error = f"right motor error during stop--detail {e}"
                self.right_handle_error(error)
            finally:
                if (len(self.right_error_counts) and self.a == 0) or 5 in self.right_error_counts:
                    self.right_log_errors()
                    break

        self.left_error_counts = []
        self.left_error_messages = []
        self.left_error_log = "right motor log"
        self.a = 1

        while True:
            try:
                self.left_PWM.value = 0
                self.left_in1.on()
                self.left_in2.on()
                self.a = 0
                break
            except Exception as e:
                error = f"left motor error during stop--detail {e}"
                self.left_handle_error(error)
            finally:
                if (len(self.left_error_counts) and self.a == 0) or 5 in self.left_error_counts:
                    self.left_log_errors()
                    break
        
        self.judge_error()

    def release(self):
        self.right_error_counts = []
        self.right_error_messages = []
        self.right_error_log = "right motor log"
        self.a = 1

        while True:
            try:
                self.right_in1.off()
                self.right_in2.off()
                self.a = 0
                break
            except Exception as e:
                error = f"right motor error during release--detail {e}"
                self.right_handle_error(error)
            finally:
                if (len(self.right_error_counts) and self.a == 0) or 5 in self.right_error_counts:
                    self.right_log_errors()
                    break

        self.left_error_counts = []
        self.left_error_messages = []
        self.left_error_log = "right motor log"
        self.a = 1

        while True:
            try:
                self.left_in1.off()
                self.left_in2.off()
                self.a = 0
                break
            except Exception as e:
                error = f"left motor error during release--detail {e}"
                self.left_handle_error(error)
            finally:
                if (len(self.left_error_counts) and self.a == 0) or 5 in self.left_error_counts:
                    self.left_log_errors()
                    break
        
        self.judge_error()

    def right_handle_error(self, error):
        if str(error) not in self.right_error_messages:
            self.right_error_messages.append(str(error))
            self.right_error_counts.append(1)
        else:
            index = self.right_error_messages.index(str(error))
            self.right_error_counts[index] += 1

    def left_handle_error(self, error):
        if str(error) not in self.left_error_messages:
            self.left_error_messages.append(str(error))
            self.left_error_counts.append(1)
        else:
            index = self.left_error_messages.index(str(error))
            self.left_error_counts[index] += 1

    def right_log_errors(self):
        list = []
        for count, message in zip(self.right_error_counts, self.right_error_messages):
            list.append(f"{count}*{message}")
        if self.a == 0:
            self.right_error_log = ",".join(list)
        elif 5 in self.right_error_counts:
            if len(list) == 1:
                self.right_error_log = f"right motor:Error--{list[0]}"
            else:
                index = self.right_error_counts.index(5)
                result = list[:index] + list[index + 1:]
                result = ",".join(result)
                self.right_error_log = f"right motor:Error--{list[index]} other errors--{result}"

    def left_log_errors(self):
        list = []
        for count, message in zip(self.left_error_counts, self.left_error_messages):
            list.append(f"{count}*{message}")
        if self.a == 0:
            self.left_error_log = ",".join(list)
        elif 5 in self.left_error_counts:
            if len(list) == 1:
                self.left_error_log = f"left motor:Error--{list[0]}"
            else:
                index = self.left_error_counts.index(5)
                result = list[:index] + list[index + 1:]
                result = ",".join(result)
                self.left_error_log = f"left motor:Error--{list[index]} other errors--{result}"

    def judge_error(self):
        if self.right_error_counts:
            if self.left_error_counts:
                self.error_log=self.right_error_counts+","+self.left_error_log
            else:
                self.error_log=self.right_error_log
        else:
            if self.left_error_counts:
                self.error_log=self.left_error_log
        
        if 5 in [self.left_error_counts,self.right_error_counts]:
            raise RuntimeError
                
