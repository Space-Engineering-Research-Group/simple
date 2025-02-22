import cv2
from picamera2 import Picamera2
from abc import ABC,abstractmethod
from time import sleep
from datetime import datetime as dt

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

                # 出力ファイル名設定
                date = dt.now().strftime("%Y%m%d_%H%M")
                path = "./" + date + ".mp4"

                # 出力ファイル設定
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
                self.out = cv2.VideoWriter(path, fourcc, fps, (width, height))
                if not self.out.isOpened():
                    raise RuntimeError("Failed to open VideoWriter")
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
                while True:
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
                self.out.write(frame)
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
                img=cv2.drawContours(frame, contour, -1, (0, 255, 0), 3)
                self.out.write(img)
                self.a = 0
                break
            except Exception as e:
                error = f"camera error during cone hozon -- detail {e}"
                self.handle_error(error)
            finally:
                if (len(self.error_counts) and self.a == 0) or 5 in self.error_counts:
                    self.log_errors()
            sleep(1)
    
    def parachute_hozon(self, frame,yellow_lower,yellow_upper):
        self.error_counts = []
        self.error_messages = []
        self.error_log = "camera:Error"
        self.a = 1
        self.ini = False

        while True:
            try:
                img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(img_hsv, yellow_lower, yellow_upper) 
                mask = cv2.medianBlur(mask, 11)
                mask[0, :] = 0            
                mask[-1, :] = 0            
                mask[:, 0] = 0            
                mask[:, -1] = 0 
                mask=cv2.Canny(mask,80.0,175.0)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    cv2.drawContours(frame, contours, -1, (255,0, 0), 3)
                self.out.write(frame)
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
