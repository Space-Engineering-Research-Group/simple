
from .camera import *
from .gps import *
from .motor import *
from .cds import *
from .servo import *
from time import sleep,time

cds=Cds()
#明るさの閾値は曇りの日に明るさを取得して決める
brightness_threshold=0.3
#ピンの値は回路班が後で決めるので仮の値
servo=Servo(12)

gps=Gps()
gps_deta=[]
goal_lat = 0
goal_lon = 0

camera=Camera()
width,height=camera.get_size()
center=width/2
frame_area=width*height

#ここの具体的な値はコーンの検査をして考える。
lower_red1 = np.array([0, 100, 100])   # 下の範囲1 (0〜10度)
upper_red1 = np.array([10, 255, 255])  # 上の範囲1
lower_red2 = np.array([170, 100, 100]) # 下の範囲2 (170〜180度)
upper_red2 = np.array([180, 255, 255]) # 上の範囲2
#赤いコーンの座標をここに書く。大会当日にかく

#pin,pwmの値は決まった
rdir_1=35
rdir_2=37
rPWM=33
ldir_1=38
ldir_2=40
lPWM=36
motors=Motor(rdir_1,rdir_2,rPWM,ldir_1,ldir_2,lPWM)

#なんとなく起動してから箱に入れるまでの時間。これじゃしょぼそうだから、明るさが低いところから高いところに行くのと、高いところから低いところに行くのを設楽っていう風にしてもいい。これは、箱が完全に密封されている想定。
sleep(20)

while True:
    bright=cds.get_brightness()
    if bright > brightness_threshold:
        break

    sleep(2)
    
#明るさを検知してから３秒後にgpsでz軸の速度を取得し始める。（3秒は何となく）
speeds=[300,300]
while True:
    speeds.append(gps.get_speed_z())
    a=0
    for i in speeds[-3:]:
        if i<0.5:
            a=a+1
    
    if a==3:
        break
    #個々の数字も場合によっては変える。
    sleep(2)

servo.rotate()
sleep(2)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ここでパラシュートの回避

while True:
    latitude, longitude = gps.get_coordinate_xy()
    move_direction = gps.move_direction()

    distance = get_distance(goal_lat,goal_lon,latitude,longitude) 
    #多分ここ間違ってる
    distance = distance - 4
    #ここはgpsの誤差を見て決める。出来るだけ近くに行けるような値にする。
    if distance <= 5:
        break
    rotation_angle = get_rotation_angle(goal_lat,goal_lon,latitude,longitude,move_direction)
    
    #ここに、回転を行うコードを書く

kazu=1

while True:
    if kazu ==1:
        p=0
        while True:
            p=p+1
            frame=camera.get_frame()
            contour=find_cone(frame,lower_red1,upper_red1,lower_red2,upper_red2)
            if contour:
                judge=judge_cone(contour,frame_area)
                if judge == True:
                    break

            #ここの数字は、カメラの画角、モーターの回転するのにかかる秒数、後はカメラのFPS?をかんがみてきめる　　
            if p==24:
                motors.stop()
                print("コーンが見つかりません")
                import sys
                sys.exit()            
            #ここの数字は上をきじゅんにして、何秒間に一回撮影する必要があるのかとかを考える。
            sleep(5)

    elif kazu == 2:
        g=True #エラーって感じのところはgを使って抜け出すようにする。
        m=False #コーンに接近成功した場合は、mで判断するようにする。
        while m:
        
            if sign==1:
                motors.turn_left()
            elif sign==-1:
                motors.turn_right()
            sign=-1
            while sign!=0:
                frame=camera.get_frame()
                contour=find_cone(frame,lower_red1,upper_red1,lower_red2,upper_red2)
                if contour is None:
                    g=False
                    break
                judge=judge_cone(contour)
                if judge is False:
                    g=False
                    break
                sign=get_distance(contour,center)
                if sign==0:
                    break
                #ここの回転方向が正しいのかをしっかり確認するようにする。また、回転スピードなども考えるようにする。
                elif sign==1:
                    motors.turn_left()
                    #ここの秒数も適当
                    sleep(2)
                else :
                    motors.turn_right()
                    #個々の秒数も適当
                    sleep(2)
                        
            if g is False:
                kazu=1
                break

            motors.forward()  
            start_time=time()
            while time()-start_time<5:
                frame=camera.get_frame()
                contour=find_cone(frame,lower_red1,upper_red1,lower_red2,lower_red2)
                if contour is None:
                    g=False
                    break
                judge=judge_cone(contour,frame_area)
                if judge is False:
                    g=False
                    break

                result=to_stop(contour,frame_area)
                if result:
                    m=True
                    break
                #個々の秒数は適当
                sleep(1)
            if g is False:
                kazu=1
                break
            if m:
                kazu=3
                break
    else:
        #ここで終了したことを送る。
        break
#エラー起きてるけど、finallyとか使うのは確実なのでとりあえずつけとく
finally:        
    motors.stop()
    gps.run_gps()
    camera.release()
    gps.delete()   