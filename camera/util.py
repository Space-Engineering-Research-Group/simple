import cv2
import numpy as np

def mask(frame,lower_red,upper_red):
    hsv_image=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    #ここの変数二つの定義を忘れない
    mask=cv2.inRange(hsv_image,lower_red,upper_red)
    #かネールサイズは実験で決める（これは仮の値）
    mask=cv2.medianBlur(mask,11)
    return mask

def get_countour(mask,frame_width):
    #第２引数と第三引数は機能を鑑みて変える
    countours,_=cv2.findContours(mask,cv2.RETA_TREE,cv2.CHAIN_APPROX_SIMPLE)
    max_countour=max(countours,key=cv2.countourArea)
    M=cv2.moments(max_countour)
    if M["m00"] !=0:
        cx=int(M["m10"]/M["m00"])
        distance=cx-frame_width
        return distance
    else:
        #whileで１００００より小さくなったら抜け出せるようにするプログラムを書く
        return 10000