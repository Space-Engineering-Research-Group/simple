import cv2
import numpy as np

def mask(frame,lower_red,upper_red):
    hsv_image=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    #ここの変数二つの定義を忘れない
    mask=cv2.inRange(hsv_image,lower_red,upper_red)
    #かネールサイズは実験で決める（これは仮の値）
    mask=cv2.medianBlur(mask,11)
    #第２引数と第三引数は機能を鑑みて変える
    countours,_=cv2.findContours(mask,cv2.RETA_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #ここでコーンの輪郭を導き出して、それをもとに面積（ピクセル数）を求めたり、重心を求めたりする
    return max(countours,key=cv2.countourArea)

def get_distance(max_countour,x):
    M=cv2.moments(max_countour)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        dx=cx-x
        if -50>x:
            sign=-1
            dx=-dx
        elif x>50:
            sign=1
        else:
            sign=0
        
        return (sign,dx)
    else:
        #0になるときはあんまりないと思うからこれ書くかしょうじきちょっとまよってる。処理をするんだとしたら３６０少しずつ回りながらコーンがあるところまで回転かな
        return 10000

