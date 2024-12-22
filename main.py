from .camera import *
from .gps import *
from .motor import *
from gpiozero.pins.pigpio import PiGPIOFactory
from .cds import *
from .servo import *
from .xbee import *
from time import sleep,time


#左から順に光センサ、GPS、カメラ、モーター、サーボモーター、xbeeが生きてたらTrueを示すようにする。
tools=[True,True,True,True,True,True]
#plan1は機体の落下、着地まで
plan1="A"
#plan2はパラシュートを回避するシーン
plan2="A"
#plan3は機体がGPSとカメラを使ってコーンに近づくシーン
plan3="A"


ins_error=[]
try:
    cds=Cds()
except RuntimeError:
        tools[0]=False
finally:
    if cds.error_counts:
        ins_error.append(cds.error_log)


#明るさの閾値は曇りの日に明るさを取得して決める
brightness_threshold=0.3
#ピンの値は回路班が後で決めるので仮の値

try:
    servo=Servo(12)
except RuntimeError:
    tools[4]=False
finally:
    if servo.error_counts:
        ins_error.append(servo.error_log)



try:
    gps=Gps()
except RuntimeError:
    tools[1]=False
finally:
    if gps.error_counts:
        ins_error.append(gps.error_log)

gps_deta=[]
#ここは大会の時に測る。
goal_lat = 0
goal_lon = 0
ground=0

width=640
height=480
FPS=10
center=width/2
frame_area=width*height
try:
    camera=Camera(width,height,FPS)
except RuntimeError:
    tools[2]=False
finally:
    if camera.error_counts:
        ins_error.append(camera.error_log)


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

factory = PiGPIOFactory()

try:
    motors=Motor(rdir_1,rdir_2,rPWM,ldir_1,ldir_2,lPWM,factory)
except Exception :
    tools[3]=False
finally:
    if motors.error_counts:
        ins_error.append(motors.error_log)

try:
    xbee=Xbee()
except RuntimeError:
    tools[5]=False
finally:
    if xbee.error_counts:
        ins_error.append(xbee.error_log)

#ここで、ログを送信する
ins_log=[1,tools[0],tools[1],tools[2],tools[3],tools[4],tools[5],ins_error]
xbee.xbee_send(ins_log,"1")


bright_ness_judge=False
while True:
    if tools[0] is False:
        if tools[1] is True:
            plan1="B"
        else:
            plan1="D"
    else:
        if tools[1] is False:
            plan1="C"

    if plan1 in ["A","C"]:
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
                    except RuntimeError :
                        tools[0]=False
                        
                
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
    
    result=None

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
                motors.turn_right()
                for i in range(24):
                    frame=camera.get_frame()
                    contour=find_cone(frame,lower_red1,upper_red1,lower_red2,upper_red2)
                    if contour:
                        judge=judge_cone(contour,frame_area)
                        if judge == True:
                            kazu=2
                            break

                    #ここの数字は、カメラの画角、モーターの回転するのにかかる秒数、後はカメラのFPS?をかんがみてきめる　　
                    if i==23:
                        motors.stop()
                        #xbeeで回転してもコーンが見つかりません見たいなのを送るようにする。
                        motors.forward()
                        sleep(4)
                                 
                        #ここの数字は上をきじゅんにして、何秒間に一回撮影する必要があるのかとかを考える。
                    sleep(0.1)

            elif kazu == 2:
                g=True #エラーって感じのところはgを使って抜け出すようにする。
                
                while True:
                    sign=-1
                    while sign!=0:
                        frame=camera.get_frame()
                        contour=find_cone(frame,lower_red1,upper_red1,lower_red2,upper_red2)
                        if contour == None:
                            g=False
                            break
                        judge=judge_cone(contour,frame_area)
                        if judge == False:
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
                        
                    if g == False:
                        kazu=1
                        break

                    motors.forward()  
                    start_time=time()
                    while time()-start_time<5:
                        frame=camera.get_frame()
                        contour=find_cone(frame,lower_red1,upper_red1,lower_red2,lower_red2)
                        if contour == None:
                            g=False
                            break
                        judge=judge_cone(contour,frame_area)
                        if judge == False:
                            g=False
                            break

                        result=to_stop(contour,frame_area)
                        if result:
                            break
                        #個々の秒数は適当
                        sleep(1)
                    if g == False:
                        kazu=1
                        break
                    if result ==True:
                        kazu=3
                        break
            else:
                #ここで終了したことを送る。
                break

    except RuntimeError as e:
        #xbeeで送信する。
        import sys
        sys.exit(1)
    except Exception as e:
        #xbeeで送信する。
        import sys
        sys.exit(1)
#エラー起きてるけど、finallyとか使うのは確実なのでとりあえずつけとく
finally:        
    motors.stop()
    gps.run_gps()
    camera.release()
    gps.delete()   