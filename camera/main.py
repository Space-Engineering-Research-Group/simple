import cv2
from picamera2 import Picamera2
from abc import ABC,abstractmethod
from time import sleep
from datetime import datetime as dt
import os

class ICamera(ABC):
    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def handle_error(self):
        pass

    @abstractmethod
    def log_errors(self):
        pass

class Camera(ICamera):
    def __init__(self, width, height, fps):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "camera:Error"
        self.oya_cone_dir="/home/spacelab/Pictures/cone_2024/"
        self.oya_parachute_dir="/home/spacelab/Pictures/parachute_2024/"
        self.a = 1
        self.ini=True
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

                date=dt.now().strftime("%Y%m%d_%H%M")
                self.save_cone_dir=os.path.join(self.oya_cone_dir,date)
                self.save_parachute_dir=os.path.join(self.oya_parachute_dir,date)
                os.mkdir(self.save_cone_dir)
                os.mkdir(self.save_parachute_dir)
                self.a = 0
                break
            except Exception as e:
                error = f"camera: Error initialization -- detail {e}"
                self.handle_error(error)
            finally:
                if (len(self.error_messages) and self.a == 0) or 5 in self.error_counts:
                    self.log_errors()
                    break
            sleep(1)

    def get_frame(self):
        self.error_counts=[]
        self.error_messages=[]
        self.error_log="camera:Error"
        self.a=1
        self.ini=False

        while True:
            try:
                frame = self.capture.capture_array()
                if frame is not None:
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    self.a=0
                    return frame_bgr
                else:
                    raise RuntimeError("Failed to capture a frame from the camera.")
            except Exception as e:
                error=f"camera error during getting frame--detail{e}"
                self.handle_error(error)

                        
            finally:
                if (len(self.error_counts)and self.a==0) or 5 in self.error_counts:
                    self.log_errors()
            sleep(1)
                
    def frame_hozon(self,frame):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "camera:Error"
        self.a = 1
        self.ini = False

        while True:
            try:
                date = dt.now().strftime("%Y%m%d_%H%M%S")
                path = os.path.join(self.save_cone_dir, date + ".jpg")
                cv2.imwrite(path, frame)
                self.a = 0
                break
            except Exception as e:
                error = f"camera error during frame hozon -- detail {e}"
                self.handle_error(error)
            finally:
                if (len(self.error_counts) and self.a == 0) or 5 in self.error_counts:
                    self.log_errors()              
            sleep(1)


    def cone_hozon(self, frame, contour):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "camera:Error"
        self.a = 1
        self.ini = False

        while True:
            try:
                date=dt.now().strftime("%Y%m%d_%H%M%S")
                path=os.path.join(self.save_cone_dir,date+".jpg")
                img=cv2.drawContours(frame, contour, -1, (0, 255, 0), 3)
                cv2.imwrite(path,img)
                self.a = 0
                break
            except Exception as e:
                error = f"camera error during cone hozon -- detail {e}"
                self.handle_error(error)
            finally:
                if (len(self.error_counts) and self.a == 0) or 5 in self.error_counts:
                    self.log_errors()
            sleep(1)
    
    def parachute_hozon(self, frame):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "camera:Error"
        self.a = 1
        self.ini = False
        while True:
            try:
                date = dt.now().strftime("%Y%m%d_%H%M%S")
                path = os.path.join(self.save_parachute_dir, date + ".jpg") 
                cv2.imwrite(path,frame)
                self.a = 0
                break
            except Exception as e:
                error = f"camera error during parachute hozon -- detail {e}"
                self.handle_error(error)
            finally:
                if (len(self.error_counts) and self.a == 0) or 5 in self.error_counts:
                    self.log_errors()
            sleep(1)
    

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
            if self.ini==False:
                raise RuntimeError
