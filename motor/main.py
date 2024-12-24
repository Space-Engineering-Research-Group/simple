from gpiozero import PWMOutputDevice, DigitalOutputDevice
from abc import ABC, abstractmethod
from time import sleep

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
    def __init__(self, rdir_1, rdir_2, rPWM, ldir_1, ldir_2, lPWM, factory):
        self.right_error_counts = []
        self.right_error_messages = []
        self.right_error_log = "right motor:Error"
        self.right_initialized = False

        self.left_error_counts = []
        self.left_error_messages = []
        self.left_error_log = "left motor:Error"
        self.left_initialized = False

        while not self.right_initialized:
            try:
                self.right_in1 = DigitalOutputDevice(rdir_1, pin_factory=factory)
                self.right_in2 = DigitalOutputDevice(rdir_2, pin_factory=factory)
                self.right_PWM = PWMOutputDevice(rPWM, pin_factory=factory)
                self.right_initialized = True
            except GPIOPinInUse as e:
                error = f"right motor:Error initializing right motor--detail{e}"
                self.handle_error(error, "right")
            except Exception as e:
                error = f"right motor:Unexpected error during initialization--detail{e}"
                self.handle_error(error, "right")
            finally:
                if (len(self.right_error_messages) and not self.right_initialized) or 5 in self.right_error_counts:
                    self.log_errors("right")
                sleep(1)

        while not self.left_initialized:
            try:
                self.left_in1 = DigitalOutputDevice(ldir_1, pin_factory=factory)
                self.left_in2 = DigitalOutputDevice(ldir_2, pin_factory=factory)
                self.left_PWM = PWMOutputDevice(lPWM, pin_factory=factory)
                self.left_initialized = True
            except GPIOPinInUse as e:
                error = f"left motor:Error initializing left motor--detail{e}"
                self.handle_error(error, "left")
            except Exception as e:
                error = f"left motor:Unexpected error during initialization--detail{e}"
                self.handle_error(error, "left")
            finally:
                if (len(self.left_error_messages) and not self.left_initialized) or 5 in self.left_error_counts:
                    self.log_errors("left")
                sleep(1)

        self.right_PWM.value = 1
        self.left_PWM.value = 1

    def forward(self, speed=1):
        self.right_PWM.value = speed
        self.left_PWM.value = speed

        self.right_in1.on()
        self.right_in2.off()

        self.left_in1.off()
        self.left_in2.on()

    def turn_right(self, speed=1):
        self.right_PWM.value = speed
        self.left_PWM.value = speed

        self.right_in1.off()
        self.right_in2.on()

        self.left_in1.off()
        self.left_in2.on()

    def turn_left(self, speed=1):
        self.right_PWM.value = speed
        self.left_PWM.value = speed

        self.right_in1.on()
        self.right_in2.off()

        self.left_in1.on()
        self.left_in2.off()

    def backward(self, speed=1):
        self.right_PWM.value = speed
        self.left_PWM.value = speed

        self.right_in1.off()
        self.right_in2.on()

        self.left_in1.on()
        self.left_in2.off()

    def stop(self):
        self.right_PWM.value = 0
        self.left_PWM.value = 0

        self.right_in1.on()
        self.right_in2.on()

        self.left_in1.on()
        self.left_in2.on()

    def release(self):
        self.right_in1.off()
        self.right_in2.off()

        self.left_in1.off()
        self.left_in2.off()

    def handle_error(self, error, motor_side):
        if motor_side == "right":
            if str(error) not in self.right_error_messages:
                self.right_error_messages.append(str(error))
                self.right_error_counts.append(1)
            else:
                index = self.right_error_messages.index(str(error))
                self.right_error_counts[index] += 1
        elif motor_side == "left":
            if str(error) not in self.left_error_messages:
                self.left_error_messages.append(str(error))
                self.left_error_counts.append(1)
            else:
                index = self.left_error_messages.index(str(error))
                self.left_error_counts[index] += 1

    def log_errors(self, motor_side):
        if motor_side == "right":
            error_list = []
            for count, message in zip(self.right_error_counts, self.right_error_messages):
                error_list.append(f"{count}*{message}")
            if self.right_initialized:
                self.right_error_log = ",".join(error_list)
            elif 5 in self.right_error_counts:
                if len(error_list) == 1:
                    self.right_error_log = f"right motor:Error--{error_list[0]}"
                else:
                    index = self.right_error_counts.index(5)
                    result = error_list[:index] + error_list[index + 1:]
                    result = ",".join(result)
                    self.right_error_log = f"right motor:Error--{error_list[index]} other errors--{result}"
                raise RuntimeError
        elif motor_side == "left":
            error_list = []
            for count, message in zip(self.left_error_counts, self.left_error_messages):
                error_list.append(f"{count}*{message}")
            if self.left_initialized:
                self.left_error_log = ",".join(error_list)
            elif 5 in self.left_error_counts:
                if len(error_list) == 1:
                    self.left_error_log = f"left motor:Error--{error_list[0]}"
                else:
                    index = self.left_error_counts.index(5)
                    result = error_list[:index] + error_list[index + 1:]
                    result = ",".join(result)
                    self.left_error_log = f"left motor:Error--{error_list[index]} other errors--{result}"
                raise RuntimeError