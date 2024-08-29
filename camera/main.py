import cv2
import numpy as np

from abc import ABC,abstractmethod

class ICamera(ABC):

    @abstractmethod
    def get_frame(self):
        pass


class Camera(ICamera):

    def __init__(self):
        self.cap=cv2.VideoCapture(0)
        self.width =self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    def get_frame(self):
        self.ret,self.frame=self.cap.read()

        if self.ret:
            return self.frame
        #ここのエラー処理を忘れないようにする（後で考える）
        return np.array([])
    