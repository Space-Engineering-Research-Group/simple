import cv2
from picamera2 import Picamera2
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
    def __init__(self, width, height, fps):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "camera:Error"
        self.a = 1
        while True:
            try:
                self.capture=Picamera2()
                # 解像度とFPSを設定
                config = self.capture.create_preview_configuration(
                    main={"size": (width, height)},  # 解像度
                    controls={"FrameRate": fps}  # FPS
                )
                self.capture.configure(config)
                self.capture.start()
                self.a = 0
                break
            except Exception as e:
                error = f"camera: Error initialization -- detail {e}"
                self.handle_error(error)
            finally:
                if (len(self.error_messages) and self.a == 0) or 5 in self.error_counts:
                    self.log_errors()
                    break

    def get_frame(self):
        self.error_counts=[]
        self.error_messages=[]
        self.error_log="camera:Error"
        self.a=1

        while True:
            try:
                while True:
                    frame = self.capture.capture_array()
                    if frame is not None:
                        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        self.a=0
                        return frame
                    else:
                        raise RuntimeError("Failed to capture a frame from the camera.")
            except Exception as e:
                error=f"camera error during getting frame--detail{e}"
                self.handle_error(error)

                        
            finally:
                if (len(self.error_counts)and self.a==0) or 5 in self.error_counts:
                    self.log_errors()

                

    

    def release(self):
        if self.capture is not None:
            self.capture.stop()

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
            self.error_log = "camera:Error--"+",".join(error_list)
        elif 5 in self.error_counts:
            if len(error_list) == 1:
                self.error_log=f"camera:Error--{error_list[0]}"
            else:
                index = self.error_counts.index(5)
                result = error_list[:index] + error_list[index + 1:]
                result = ",".join(result)
                self.error_log = f"camera:Error--{error_list[index]} other errors--{result}"
                raise RuntimeError
