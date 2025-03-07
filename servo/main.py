import abc
from gpiozero import Servo
from time import sleep

class Iservo(abc.ABC):
     @abc.abstractmethod
     def rotate(self):
          pass

     @abc.abstractmethod     
     def stop(self):
          pass

     @abc.abstractmethod     
     def handle_error(self):
          pass

     @abc.abstractmethod     
     def log_errors(self):
          pass

class Myservo(Iservo):
     def __init__(self, pin,factory):
          self.error_counts = []
          self.error_messages = []
          self.error_log = "Servo Error Log"
          self.a = 1
          self.ini=True
          while True:
               try:
                    self.servo = Servo(pin,pin_factory=factory)
                    self.a = 0
                    break
               except IOError as e:
                    error = f"Servo: Error initializing Servo--detail {e}"
                    self.handle_error(error)
               except Exception as e:
                    error = f"Servo: Unexpected error during initialization --detail {e}"
                    self.handle_error(error)
               finally:
                    if (len(self.error_messages) and self.a == 0) or 5 in self.error_counts:
                         self.log_errors()
                         break
               sleep(1)

     def rotate(self):
          self.error_counts = []
          self.error_messages = []
          self.error_log = "Servo Error Log"
          self.a = 1
          self.ini=False
          while True:
               try:
                    self.servo.value = -1
                    self.a = 0
                    break
               except IOError as e:
                    error = f"Servo: Error rotating Servo--detail {e}"
                    self.handle_error(error)
               except Exception as e:
                    error = f"Servo: Unexpected error while rotating Servo --detail {e}"
                    self.handle_error(error)
               finally:
                    if (len(self.error_messages) and self.a == 0) or 5 in self.error_counts:
                         self.log_errors()

               sleep(1)

     def stop(self):
          self.error_counts = []
          self.error_messages = []
          self.error_log = "Servo Error Log"
          self.a = 1
          self.ini=False
          while True:
               try:
                    self.servo.value = 0
                    self.a = 0
                    break
               except IOError as e:
                    error = f"Servo: Error stopping Servo--detail {e}"
                    self.handle_error(error)
               except Exception as e:
                    error = f"Servo: Unexpected error while stopping Servo --detail {e}"
                    self.handle_error(error)
               finally:
                    if (len(self.error_messages) and self.a == 0) or 5 in self.error_counts:
                         self.log_errors()
               sleep(1)

     def handle_error(self, error):
          if str(error) not in self.error_messages:
               self.error_messages.append(str(error))
               self.error_counts.append(1)
          else:
               index = self.error_messages.index(str(error))
               self.error_counts[index] += 1

     def log_errors(self):
          error_list = []
          for count, message in zip(self.error_counts, self.error_messages):
               error_list.append(f"{count}*{message}")
          if self.a == 0:
               self.error_log = ",".join(error_list)
          elif 5 in self.error_counts:
               if len(error_list) == 1:
                    self.error_log = f"Servo: Error--{error_list[0]}"
               else:
                    index = self.error_counts.index(5)
                    result = error_list[:index] + error_list[index + 1:]
                    result = ",".join(result)
                    self.error_log = f"Servo: Error--{error_list[index]} other errors--{result}"
               if self.ini==False:
                    raise RuntimeError