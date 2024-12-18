import cv2
from abc import ABC,abstractmethod

class ICamera(ABC):
    @abstractmethod
    def get_size(self):
        pass

    def get_frame(self):
        pass

    def release(self):
        pass


class Camera(ICamera):
    def __init__(self):
        self.capture=cv2.VideoCapture(0)
        if not self.capture.isOpened():
            raise IOError("Failed to open the camera.")
    def get_size(self):
        width =self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height=self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return (width,height)

    def get_frame(self):
        ret,frame=self.capture.read()
        if ret:
            return frame
        else:
            raise RuntimeError("Failed to capture a frame from the camera.")
    
    def release(self):
        if self.capture.isOpened():
            self.capture.release