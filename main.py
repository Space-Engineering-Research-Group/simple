from .camera import *
from .gps import *
from .motor import *

#~~~~~センサ、サーボの部分は飛ばす~~~~

#ピンの具体的な値は後で決める
forward_left_pin=1
back_left_pin=1
forward_right_pin=1
back_right_pin=1
motors=motor(forward_left_pin,back_left_pin,forward_right_pin,ack_right_pin)
gps=Gps()
gps_deta=[]
camera=Camera()
width,height=camera.get_frame()
frame_area=width*height
#ここの具体的な値はコーンの検査をして考える。大会前日とか？
lower_red=[170,100,255]
upper_red=[180,255,255]

#モーターが回転するコード
i=0
while True:
    i=i+1
    frame=camera.get_frame()
    contour=find_cone(frame,lower_red,upper_red)
    if len(contour):
        break
        #モーターをストップさせるコード
    if i==4:
        raise 
    
while True:
    frame=camera.get_frame()
    contour=find_cone(frame,lower_red,upper_red)
    result=to_stop(contour,frame_area)
    if result:
        