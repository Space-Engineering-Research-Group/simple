import cv2
from abc import ABC,abstractmethod

class ICamera(ABC):
    @abstractmethod
    def get_size(self):
        pass
    
    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def release(self):
        pass

class Camera(ICamera):
    def __init__(self, width, height, FPS):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "camera:Error"
        self.a = 1
        while True:
            try:
                self.capture = cv2.VideoCapture(0)
                if not self.capture.isOpened():
                    raise IOError("camera: Failed to open the camera.")
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                self.capture.set(cv2.CAP_PROP_FPS, FPS)
                self.a = 0
                break
            except IOError as e:
                error = f"camera: Error initializing camera -- detail {e}"
                self.handle_error(error)
            except Exception as e:
                error = f"camera: Unexpected error during initialization -- detail {e}"
                self.handle_error(error)
            finally:
                if (len(self.error_messages) and self.a == 0) or 5 in self.error_counts:
                    self.log_errors()
                    break

    def get_frame(self):
        self.error_count=0
        self.error_log="camera:Error"
        error = "camera: Failed to capture a frame from the camera."
        while True:
            try:
                while True:
                    ret, frame = self.capture.read()
                    if ret:
                        return frame
                    else:
                        self.error_count += 1

                        if self.error_count == 5:
                            raise RuntimeError
                        
            finally:
                if self.error_count:
                    self.error_log=f"{self.error_count}*{error}"

                

    

    def release(self):
        if self.capture is not None and self.capture.isOpened():
            self.capture.release()

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
            if len(list) == 1:
                self.error_log=f"camera:Error--{list[0]}"
            else:
                index = self.error_counts.index(5)
                result = error_list[:index] + error_list[index + 1:]
                result = ",".join(result)
                self.error_log = f"camera:Error--{error_list[index]} other errors--{result}"
                raise RuntimeError