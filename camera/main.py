import cv2
import numpy as np

from abc import ABC,abstractmethod

class ICamera(ABC):
    @abstractmethod
    def get_frame(self):
        pass


class Camera(ICamera):
    def __init__(self):
        self.capture=cv2.VideoCapture(0)
    
    def get_size(self):
        width =self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height=self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return (width,height)

    def get_frame(self):
        ret,frame=self.cap.read()
        if ret:
            return frame
        #ここのエラー処理を忘れないようにする（後で考える）
        return np.array([])
    