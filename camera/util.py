import cv2
import numpy as np

def find_cone(frame,lower_red1,upper_red1,lower_red2,upper_red2):
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)
    mask2=cv2.inRange(img_hsv,lower_red2,upper_red2)
    mask=cv2.bitwise_or(mask1,mask2)          
    mask = cv2.medianBlur(mask, 11)
    mask[0, :] = 0            
    mask[-1, :] = 0            
    mask[:, 0] = 0            
    mask[:, -1] = 0 
    mask=cv2.Canny(mask,80.0,175.0)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # 最大面積のコンターを返す
        max_contour = max(contours, key=cv2.contourArea)
        return max_contour
    return None

def find_parachute(frame,lower_yellow,upper_yellow,center,frame_area,phase):
    img_hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img_hsv, lower_yellow, upper_yellow)       
    mask = cv2.medianBlur(mask, 11)

    yellow_pixels=np.sum(mask==255)
    yellow_ratio=yellow_pixels/frame_area

    threshold=0.03
    if yellow_ratio>=threshold:
        if phase==0:
            return True
        elif phase==1:
            left_half = mask[:, :center]
            right_half = mask[:, center:]   

            left_yellow_count = np.sum(left_half == 255)
            right_yellow_count = np.sum(right_half == 255)

            if left_yellow_count > right_yellow_count:
                return [-1,True]
            else:
                return [1,True]
    else:
        if phase==0:
            return False
        else:
            return [None,False]

def judge_cone(contour,frame_area):
    area=cv2.contourArea(contour)
    raito=(area/frame_area)*100
    #個々の値も適当
    if raito >= 0.04:
        return True
    return False

        
def get_distance(contour,x):
    M=cv2.moments(contour)
    cx = int(M["m10"] / M["m00"])
    dx=cx-x
    #ここの５０は仮の値(実験でかえる)
    if dx<-50:
        sign=-1 
    elif dx>50:
        sign=1
    else:
        sign=0
        
    return sign


def to_stop(contour,frame_area):
    #area_frameはカメラの画面全体のピクセル数事前にx*yを計算しておく
    area=cv2.contourArea(contour)
    raito=area/frame_area

    if raito >=0.8:
        return True
    return False
