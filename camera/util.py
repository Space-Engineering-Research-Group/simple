import cv2
import numpy as np

def find_cone(frame,lower_red,upper_red):
    hsv_image=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    #ここの変数二つの定義を忘れない
    mask=cv2.inRange(hsv_image,lower_red,upper_red)
    #かネールサイズは実験で決める（これは仮の値）
    mask=cv2.medianBlur(mask,11)
    #第２引数と第三引数は機能を鑑みて変える
    contours,_=cv2.findContours(mask,cv2.RETA_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    #ここでコーンの輪郭を導き出して、それをもとに面積（ピクセル数）を求めたり、重心を求めたりする
    
    for contour in contours:
        area=cv2.contourArea(contour)
        #１００の数値は適当。近づいた時のピクセル数がどのくらいになっているかが分からない。コーン全体が入らなくなったときに、どのくらいの距離にあるかを考えるべき。
        if area >100:
            return contour
        hull=cv2.convexHull(contour)
        hull_area=cv2.contourArea(hull)
        solidity=area/hull_area
        #個々の数字は実験ののち決める
        if 0.8<solidity<1.0:
            return contour
        
    return []


def get_distance(contour,x):
    M=cv2.moments(contour)
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


def to_stop(contour,area_frame):
    #area_frameはカメラの画面全体のピクセル数事前にx*yを計算しておく
    area=cv2.contourArea(contour)
    #コーンの面積が画面全体の８割を超えたら停止するためにTrueを返す
    if area>0.8*area_frame:
        return True
    return False