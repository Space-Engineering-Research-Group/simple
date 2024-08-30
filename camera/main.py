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
        if not self.capture.isOpened():
            raise RuntimeError("カメラを開けませんでした")
    def get_size(self):
        width =self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height=self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return (width,height)

    def get_frame(self):
        ret,frame=self.capture.read()
        if ret:
            return frame
        else:
            print("カメラから映像を取得できません")
            #エラーの内容はchatgptのやつコピペしただけ
            raise RuntimeError("カメラから映像を取得できません")

    def release(self):
        if self.capture.isOpened():
            self.capture.release