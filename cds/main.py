from gpiozero import MCP3008
from abc import ABC, abstractmethod
from time import sleep

class Icds(ABC):
    @abstractmethod
    def get_brightness(self):
        pass

class Cds(Icds):
    def __init__(self):
        self.error_counts = []
        self.error_messages = []
        self.error_log="cds Error Log"
        while True:
            try:
                self.cds = MCP3008(channel=0)
                a=0
                break
            except IOError as e:
                error=f"cds:Error initializing MCP3008--detail{e}"
                self.handle_error(error)
            except Exception as e:
                error=f"cds: Unexpected error during initialization --detail{e}"
                self.handle_error(error)
            finally:
                if len(self.error_messages):
                    self.log_errors()
                    
                        

            sleep(1)

    def get_brightness(self):
        self.error_counts=[]
        self.error_messages=[]
        while True:
            try:
                brightness = self.cds.value
                a=0
                if brightness < 0.0 or brightness > 1.0:
                    raise ValueError(f"cds: Brightness value out of range: {brightness}")
                return brightness
            except IOError as e:
                error=f"cds: Error reading brightness--detail{e}"
                self.handle_error('IOError', error)
            except ValueError as e:
                error=f"{e}"
                self.handle_error('ValueError', error)
            except Exception as e:
                error=f"cds: Unexpected error while reading brightness --detail{e}"
                self.handle_error('Exception', error)
            finally:
                if len(self.error_messages):
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
        if a==0:
            self.error_log=",".join(list)
        elif 5 in self.error_counts:
            index=self.error_counts.index(5)
            result=list[:index]+list[index+1:]
            result=",".join(result)
            self.error_log=f"cds:Error--{list[index]} other errors--{result}"
            raise RuntimeError
