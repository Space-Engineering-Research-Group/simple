
from .camera import *
from .gps import *
from .motor import *
from .cds import *
from .servo import *
from time import sleep,time


#左から順に光センサ、GPS、カメラが生きてたらTrueを示すようにする。
fplan=[True,True,True]
#plan1は機体の落下、着地まで
plan1="A"
#plan2は機体がGPSとカメラを使ってコーンに近づくシーン
plan2="A"

ins=["ins",True,True,True,True,True]

for i in range(4):
    try:
        cds=Cds()
        break
    except Exception as e:
        if i == 4:
            fplan[0]=False
            ins[1]=False


#明るさの閾値は曇りの日に明るさを取得して決める
brightness_threshold=0.3
#ピンの値は回路班が後で決めるので仮の値
for i in range(5):
    try:
        servo=Servo(12)
    except nantoka as e:
        if i ==4:
            ins[2]=False


for i in range(5):
    try:
        gps=Gps()
        break
    except Exception as e:
        if i is 4:
            fplan[1]=False
            ins[3]=False

gps_deta=[]
#ここは大会の時に測る。
goal_lat = 0
goal_lon = 0
ground=0

for i in range(5):
    try:
        camera=Camera()
        break
    except IOError as e:
        if i is 4:
            fplan[2]=False
            ins[4]=False

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

for i in range(4):
    try:
        motors=Motor(rdir_1,rdir_2,rPWM,ldir_1,ldir_2,lPWM)
    except nantoka as e:
        if i ==4:
            ins[5]=False
    
while True:
    if fplan[0] is False:
        if fplan[1] is True:
            plan1="B"
        else:
            plan1="D"
    else:
        if fplan[1] is False:
            plan1="C"

    if plan1 is "A" or "C":
        try:
            #なんとなく起動してから箱に入れるまでの時間。これじゃしょぼそうだから、明るさが低いところから高いところに行くのと、高いところから低いところに行くのを設楽っていう風にしてもいい。これは、箱が完全に密封されている想定。
            sleep(20)
    
            while True:
                p=0
                bright=0
                while True:
                    try:
                        bright=cds.get_brightness()
                        break
                    except ValueError as e:
                        #xbeeによる送信
                        p=p+1
                        if p==5:
                            raise ValueError ("Five consecutive abnormal values")
                        sleep(1)
                
                if bright > brightness_threshold:
                    break
                
                sleep(2)
        except ValueError as e:
            #xbeeで送信する
            fplan[0]=False
            continue
        except IOError as e:
            #xbeeで送信する。
            fplan[0]=False
            continue
        except Exception as e:
            #xbeeで送信する。
            fplan[0]=False
            continue
    
    if 
    #明るさを検知してから３秒後にgpsでz軸の速度を取得し始める。（3秒は何となく）
    dis=[300,300]
            while True:
                alt=
    
                if a==3:
                    break
                #個々の数字も場合によっては変える。
                sleep(2)

servo.rotate()
sleep(2)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ここでパラシュートの回避


kazu=1
while True:
    if fplan[1] is False:
        if fplan[2] is True:
            plan2="C"
        else:
            plan2="D"
    else:
        if fplan[2] is False:
            plan2="B"

    while True:
        latitude, longitude = gps.get_coordinate_xy()
        move_direction = gps.move_direction()

        distance = get_distance(goal_lat,goal_lon,latitude,longitude) 

        #ここはgpsの誤差を見て決める。出来るだけ近くに行けるような値にする。
        if distance <= 5:
            break
        rotation_angle = get_rotation_angle(goal_lat,goal_lon,latitude,longitude,move_direction)
    
        #ここに、回転を行うコードを書く


        try:
            o=0
            while True:
                if kazu ==1:
                    p=0
                    while True:
                        p=p+1
                        motors.turn_right()
                        for i in range(5):
                            try:
                                frame=camera.get_frame()
                                break
                            except RuntimeError as e:
                                if i is 5:
                                    #xbeeで送信
                                    fplan[2]=False
                                    raise RuntimeError(e)
                        contour=find_cone(frame,lower_red1,upper_red1,lower_red2,upper_red2)
                        if contour:
                            judge=judge_cone(contour,frame_area)
                            if judge == True:
                                kazu=2
                                break

                        #ここの数字は、カメラの画角、モーターの回転するのにかかる秒数、後はカメラのFPS?をかんがみてきめる　　
                        if p==24:
                            motors.stop()
                            #xbeeで回転してもコーンが見つかりません見たいなのを送るようにする。
                            motors.forward()
                            sleep(4)
                            break
                                 
                        #ここの数字は上をきじゅんにして、何秒間に一回撮影する必要があるのかとかを考える。
                        sleep(0.1)

                elif kazu == 2:
                    g=True #エラーって感じのところはgを使って抜け出すようにする。
                    m=False #コーンに接近成功した場合は、mで判断するようにする。
                    while True:
        
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