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

ins_error_tool=[]
ins_error=[]

#箱の中に入れるまでの時間計測する。
preparation_time=60
#光センサで明るいことを検知してから落下するまでにかかると想定する時間
fall_time=60
#光センサで判断できなかった場合に置ける処理が起動してから落下するまでにかかるだろうとする時間
land_time=480

try:
    cds=Cds()
except RuntimeError:
        tools[0]=False
finally:
    if cds.error_counts:
        ins_error_tool.append("cds")
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
        ins_error_tool.append("servo")
        ins_error.append(servo.error_log)



try:
    gps=Gps()
except RuntimeError:
    tools[1]=False
finally:
    if gps.error_counts:
        ins_error_tool.append("gps")
        ins_error.append(gps.error_log)

gps_deta=[]
#ここは大会の時に測る。
goal_lat = 0
goal_lon = 0

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
        ins_error_tool.append("camera")
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
        ins_error_tool.append("motors")
        ins_error.append(motors.error_log)

try:
    xbee=Xbee()
except RuntimeError:
    tools[5]=False
finally:
    if xbee.error_counts:
        ins_error_tool.append("xbee")
        ins_error.append(xbee.error_log)

#ここで、ログを送信する
ins_log=[1,time(),tools[0],tools[1],tools[2],tools[3],tools[4],tools[5],ins_error_tool,ins_error]
xbee.xbee_send(ins_log)

start_time=time()


#箱に入れるまでの時間を仮に一分と置き、その間ずっと明るさを取得して、xbeeで送るようにする。
while time()-start_time<preparation_time:
    #左から、フェーズ、時間、明るさ、故障した部品、エラー文
    fir_cds_log=[-1,None,None,None,None]
    try:
        fir_cds_log[1]=time()
        cds.get_brightness()
        fir_cds_log[2]=cds.brightness
    except RuntimeError:
        tools[0]=False
        raise RuntimeError
    finally:
        if len(cds.error_counts):
            fir_cds_log[4]=cds.log_errors
            if 5 in cds.error_counts:
                fir_cds_log[3]="cds"
                xbee.send(cds.error_log)



land_judge=False
start_time=time()
while land_judge==False:
    if tools[0]==False:
        plan1="B"
        notice_log=[9,"cdsが使えないため、起動してからの時間経過での着地判定に切り替えます。"]

    if plan1 =="A":
        try:
            while land_judge==False:
                notice_log=[9,"cdsを用いた落下判定を開始します。"]
                #左からフェーズ、プラン、時間、明るさ、落下判断、使えない部品、エラー文
                cds_log=[2,"A",0,None,None,None,None]
                try:
                    cds_log[1]=time()
                    if cds_log[1]-start_time>land_time:
                        land_judge=True
                        notice_log=[9,"８分間一定以上の明るさを検知できなかったため、着地したと判定する。"]
                        continue
                    cds.get_brightness()
                    cds_log[4]=cds.brightness
                    if cds.brightness < brightness_threshold:
                        cds_log[3]=True
                        start_time=time()
                        notice_log=[9,"一定以上の明るさを検知したため、１分経過したら着地したと判定"]
                        xbee.xbee_send(notice_log)
                        while time()-start_time<fall_time:
                            #左からフェーズ、時間、残り時間
                            time_log=[8,None,None]
                            now_time=time()
                            time_log[1]=now_time
                            time_log[2]=fall_time-(now_time-start_time)
                            xbee.xbee_send(time_log)
                        notice_log=[9,"１分経過したため着地したと判定"]
                        land_judge=True



                except RuntimeError :
                        tools[0]=False
                        raise RuntimeError
                finally:
                    if len(cds.error_counts):
                        cds_log[6]=cds.error_log
                        if 5 in cds.error_counts:
                            cds_log[5]="cds"
                    xbee.xbee_send(cds_log)
                
                sleep(2)
        except RuntimeError:
            continue
        
    elif  plan1=="B":
        while time()-start_time()<land_time:
            #左からフェーズ、時間、残り時間
            time_log=[8,None,None]
            now_time=time()
            time_log[1]=now_time
            time_log[2]=land_time-(now_time-start_time)
        land_judge=True
        notice_log=[9,"起動から８分間経過したため、着地したとみなす。"]
            
            
if tools[4]==True:
    notice_log=[9,"サーボモーターを用いてパラシュートの切り離しを行います。"]
    xbee.xbee.send(notice_log) 
else:
    notice_log=[9,"サーボモーターが使えないため、コードを停止します。"]
    xbee.xbee.send(notice_log)       
    import sys
    sys.exit(1)

try:            
    servo.rotate()
    #個々の時間は後で計算する
    sleep(30)
except RuntimeError:
    notice_log=[9,"サーボモーターが使えなくなったため、コードを停止します。"]

notice_log=[9,"パラシュートの切り離しを行いました。"]

if tools[2]=True:

    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ここでパラシュートの回避 4


kazu=1
gps_seikou=False
while True:
    if tools[1] is False:
        if tools[2] is True:
            plan2="C"
        else:
            plan2="D"
    else:
        if tools[2] is False:
            plan2="B"
    
    result=None
#gps
    if plan2 in ["A","B"]and gps_seikou==False:
        try:
            #左からフェーズ、時間、緯度、経度、コーンとの距離、コーンに対する角度、故障した部品、エラー文
            gps_log = [5,None,None,None,None,None,None,None,None]
            try:
                gps_log[1]=time()
                pre_lat,pre_lon = gps.get_coordinate_xy()
                gps_log[2]=pre_lat
                gps_log[3]=pre_lon
            except RuntimeError:
                tools[1]=False
                raise RuntimeError
            finally:
                if len(gps.error_counts):
                    gps_log[7]=gps.error_log
                    if 5 in gps.error_counts:
                        gps_log[6]="gps"
                xbee.xbee_send(gps_log)

                #初めからコーンが近い場合の処理     
            distance=get_distance(pre_lat,pre_lon,goal_lat,goal_lon)
            if distance<4:
                try:
                    motors.forward(1/208)
                    sleep(20)
                    motors.stop()
                    gps_seikou=True
                    continue
                except RuntimeError:
                    tools[3]=False
                    import sys
                    sys.exit(1)
                finally:    
                    if len(motors.error_counts):
                        motors_log=[7,None,motors.error_log]
                        if 5 in motors.error_counts:
                            motors_log[1]="motors"
                        xbee.xbee_send(motors)    
            else:
                try:
                    motors.turn_left(1/208)
                    sleep(30)
                    motors.stop()
                except RuntimeError:
                    tools[3]=False
                    import sys
                    sys.exit(1)
                finally:
                    if len(motors.error_counts):
                        motors_log=[7,None,motors.error_log]
                        if 5 in motors.error_counts:
                            motors_log[1]="motors"
                        xbee.xbee_send(motors)        

            stack_count = 0
            while True:
                #左からフェーズ、時間、緯度、経度、コーンとの距離、コーンに対する角度、故障した部品、エラー文
                gps_log = [5,None,None,None,None,None,None,None]    
            
                try:
                    gps_log[1] = time()
                    now_lat,now_lon = gps.get_coordinate_xy()
                    gps_log[2],gps_log[3] = now_lat, now_lon
                except RuntimeError:
                    tools[1]=False
                    raise RuntimeError
                finally:
                    if len(gps.error_counts):
                        gps_log[7]=gps.error_log
                        if 5 in gps.error_counts:
                            gps_log[6]="gps"
                    xbee.xbee_send(gps_log)    
        

                distance = get_distance(now_lat, now_lon, pre_lat, pre_lon)            

                if distance<1.4:
                    #stuckした場合の処理
                    try:
                        stack_count+=1
                        if stack_count==4:
                            import sys
                            sys.exit(1)
                        motors.backward()
                        sleep(5)  
                        motors.turn_left()
                        #秒数は計算して出す
                        sleep(90/280)
                        motors.forward()
                        sleep(5)    
                        continue
                    except RuntimeError:
                        tools[3]=False
                        import sys
                        sys.exit(1)
                    finally:
                        if len(motors.error_counts):
                            motors_log=[7,None,motors.error_log]
                            if 5 in motors.error_counts:
                                motors_log[1]="motors"
                            xbee.xbee_send(motors)

                    try:
                        gps_log[1] = time()
                        pre_lat,pre_lon = gps.get_coordinate_xy()
                        gps_log[2], gps_log[3] = pre_lat, pre_lon
                    except RuntimeError:
                        tools[1]=False
                        raise RuntimeError
                    finally:
                        if len(gps.error_counts):
                            gps[7]=gps.error_log
                            if 5 in gps.error_counts:
                                gps[6]="gps"
                        xbee.xbee_send(gps)    


                
                distance = get_distance(goal_lat, goal_lon, now_lat, now_lon)            

                #judge
                if distance<4:
                    try:
                        motors.forward(1/208)
                        sleep(20)
                        motors.stop()
                        gps_seikou=True
                        continue
                    except RuntimeError:
                        tools[3]=False
                        import sys
                        sys.exit(1)
                    finally:    
                        if len(motors.error_counts):
                            motors_log=[7,None,motors.error_log]
                            if 5 in motors.error_counts:
                                motors_log[1]="motors"
                            xbee.xbee_send(motors_log)
                if distance<2:
                    gps_seikou=True

                    if plan2 == "B": #planは適当あとで確認。
                        #カメラが壊れていた場合
                        try:
                            gps_B_lat = []
                            gps_B_lon = []
                        
                            for i in range(2):
                                lat,lon = gps.get_coordinate_xy()
                                gps_B_lat.append(lat)
                                gps_B_lon.append(lon)
                                sleep(0.1)
                            gps_B_lat_ave = sum(gps_B_lat)/2
                            gps_B_lon_ave = sum(gps_B_lon)/2    

                            distance = get_distance(gps_B_lat_ave,gps_B_lon_ave,goal_lat,goal_lon)
                            if distance<0.5:#適当
                                gps_seikou=True
                                #成功したことを送る

                            move_direction = gps.move_direction(gps_B_lat_ave,gps_B_lon_ave,goal_lat,goal_lon)
                            get_rotation_angle = get_rotation_angle(goal_lat,goal_lon,gps_B_lat_ave,gps_B_lon_ave,move_direction)   
                        except RuntimeError:
                            tools[1]=False
                            raise RuntimeError
                        finally:
                            if len(gps.error_counts):
                                gps[7]=gps.error_log
                                if 5 in gps.error_counts:
                                    gps[6]="gps"
                                xbee.xbee_send(gps)

                        try:
                            motors.turn_left(1/208)
                            sleep(4)
                            motors.stop()
                        except RuntimeError:
                            tools[3]=False
                            import sys
                            sys.exit(1)
                        finally:    
                            if len(motors.error_counts):
                                motors_log=[7,None,motors.error_log]
                                if 5 in motors.error_counts:
                                    motors_log[1]="motors"
                                xbee.xbee_send(motors)        

                try:
                    move_direction = gps.move_direction(pre_lat,pre_lon,now_lat,now_lon)
                    get_rotation_anglef = get_rotation_angle(goal_lat,goal_lon,now_lat,now_lon,move_direction)
                except RuntimeError:
                    tools[1]=False
                    raise RuntimeError
                finally:
                    if len(gps.error_counts):
                        gps[7]=gps.error_log
                        if 5 in gps.error_counts:
                            gps[6]="gps"
                            xbee.xbee_send(gps)
                
                try:
                    motors.turn_left(1/208)
                    sleep(get_rotation_angle/208)
                    motors.stop()
                    pre_lat,pre_lon = now_lat,now_lon
                except:
                    tools[3]=False
                    import sys
                    sys.exit(1) 
                finally:    
                    if len(motors.error_counts):
                        motors_log=[7,None,motors.error_log]
                        if 5 in motors.error_counts:
                            motors_log[1]="motors"
                        xbee.xbee_send(motors)        
        
        except RuntimeError:
            continue

            


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

