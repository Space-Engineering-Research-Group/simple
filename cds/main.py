from gpiozero import MCP3008
from abc import ABC, abstractmethod
from time import sleep

class Icds(ABC):
    @abstractmethod
    def get_brightness(self):
        pass

    @abstractmethod    
    def handle_error(self):
        pass

    @abstractmethod    
    def log_errors(self):   
        pass 


class Cds(Icds):
    def __init__(self):
        self.error_counts = []
        self.error_messages = []
        self.error_log="cds Error Log"
        self.a=1
        self.ini=True
        while True:
            try:
                self.cds = MCP3008(channel=0)
                self.a=0
                break
            except IOError as e:
                error=f"cds:Error initializing MCP3008--detail{e}"
                self.handle_error(error)
            except Exception as e:
                error=f"cds: Unexpected error during initialization --detail{e}"
                self.handle_error(error)
            finally:
                if (len(self.error_messages)and self.a==0)or 5 in self.error_counts:
                    self.log_errors()
                    
            sleep(1)

    def get_brightness(self):
        self.error_counts=[]
        self.error_messages=[]
        self.error_log="cds Error Log"
        self.a=1
        self.ini=False
        while True:
            try:
                self.brightness = self.cds.value
                
                if self.brightness < 0.0 or self.brightness > 1.0:
                    raise ValueError(f"Brightness value out of range")
                self.a=0
                break
            except IOError as e:
                error=f"cds: Error reading brightness--detail{e}"
                self.handle_error(error)
            except ValueError as e:
                error=f"cds: Error detail--{e}"
                self.handle_error(error)
            except Exception as e:
                error=f"cds: Unexpected error while reading brightness --detail{e}"
                self.handle_error(error)
            finally:
                if (len(self.error_messages)and self.a==0)or 5 in self.error_counts:
                    self.log_errors()
                        
            sleep(1)

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
            self.error_log="cds Error--"+",".join(list)
        elif 5 in self.error_counts:
            if len(list) == 1:
                self.error_log=f"cds:Error--{list[0]}"
            else:
                index=self.error_counts.index(5)
                result=list[:index]+list[index+1:]
                result=",".join(result)
                self.error_log=f"cds:Error--{list[index]} other errors--{result}"
            if self.ini==False:
                raise RuntimeError
