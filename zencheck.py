try:
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




    #このふぁいるは、エラーが出たら即死にしたいため、通常であればエラーを吐くようなところをsys.exit(1)としています。そこを覚えておいてください。

    #xbeeのエラーとかちゃんと追加してね


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    from camera import *
    import numpy as np
    from gps import *
    from motor import *
    from gpiozero.pins.pigpio import PiGPIOFactory
    from cds import *
    from servo import *
    from XB import *
    from raspberry_log import *
    from time import sleep,time
    from datetime import datetime, timedelta, timezone

    def mget_time():
        # 日本のタイムゾーン（UTC+9）を設定
        japan_time = datetime.now(timezone(timedelta(hours=9)))

        # 秒数を小数点以下まで取得（小数点3桁）
        seconds_with_micro = japan_time.second + japan_time.microsecond / 1_000_000

        # 何時何分小数点以下の秒数の形式で文字列を作成
        time_string = japan_time.strftime('%H時%M分') + f'{seconds_with_micro:.3f}秒'

        return time_string
    
    


    #左から順に光センサ、GPS、カメラ、モーター、サーボモーター、xbee、raspy_logもどきが生きてたらTrueを示すようにする。
    tools=[True,True,True,True,True,True,True]
    #plan1は機体の落下、着地まで
    plan1="A"
    #plan2はgpsとカメラでコーンに近づいていくシーン
    plan2="A"

    ins_error_tool=[]
    ins_error=[]

    #光センサで明るいことを検知してから落下するまでにかかると想定する時間
    fall_time=60
    #光センサで判断できなかった場合に置ける処理が起動してから落下するまでにかかるだろうとする時間
    land_time=480

    try:
        cds=Cds()
    finally:
        if len(cds.error_counts)>0:
            ins_error.append(cds.error_log)   
            if  5 in cds.error_counts:
                ins_error_tool.append("cds")
                tools[0]=False   


    #明るさの閾値は曇りの日に明るさを取得して決める
    brightness_threshold=0.3
    #ピンの値は回路班が後で決めるので仮の値
    factory = PiGPIOFactory()
    try:
        servo=Myservo(12,factory)
    finally:
        if len(servo.error_counts)>0:
            ins_error.append(servo.error_log)
            if 5 in servo.error_counts:
                ins_error_tool.append("servo")
                tools[4]=False
    
    #サーボモーターが回転する時間
    srote_time=10

    try:
        gps=Gps()
    finally:
        if len(gps.error_counts)>0:
            ins_error.append(gps.error_log)
            if 5 in gps.error_counts:
               ins_error_tool.append("gps") 
               tools[1]=False

    gps_deta=[]
    #ここは大会の時に測る。
    goal_lat = 0
    goal_lon = 0
    #以下４個は実験をして値を決める
    #planAの時は4m以内の時に成功
    A_x = 4
    #planBの時は2m以内の時に成功
    B_x = 2
    #sackの判別メートル
    s_x = 1.5
    #カメラが壊れてplanBになった時の成功
    B_x2 = 0.5


    #設定的に一番低そうなこれにする。
    width=640
    height=480
    fps=10
    center=width//2
    frame_area=width*height
    #カメラの画角（実験値）
    view_angle=120
    #ここは機体が組みあがった後に実験して決める
    parea_threshold=0.04
    try:
        camera=Camera(width,height,fps)
    finally:
        if len(camera.error_counts)>0:
            ins_error.append(camera.error_log)
            if 5 in camera.error_counts:
                ins_error_tool.append("camera")
                tools[2]=False

    #ここの具体的な値はコーンの検査をして考える。
    lower_red1 = np.array([0, 100, 70])   # 下の範囲1 (0〜10度)
    upper_red1 = np.array([10, 255, 255])  # 上の範囲1
    lower_red2 = np.array([170, 100, 70]) # 下の範囲2 (170〜180度)
    upper_red2 = np.array([180, 255, 255]) # 上の範囲2

    #パラシュートの黄色をしっかり検出出来るようにする。
    lower_yellow=np.array([20, 100, 100])
    upper_yellow=np.array([40, 255, 255])


    #pin,pwmの値は決まった
    rdir_1=19
    rdir_2=26
    rPWM=13
    ldir_1=23
    ldir_2=24
    lPWM=18

    try:
        motors=Motor(rdir_1,rdir_2,rPWM,ldir_1,ldir_2,lPWM,factory)
    finally:
        if len(motors.left_error_counts)>0 or len(motors.right_error_counts)>0:
            ins_error.append(motors.error_log)
            if 5 in motors.left_error_counts:
                ins_error_tool.append("left motor")
                tools[3]=False
            if 5 in motors.right_error_counts:
                ins_error_tool.append("right motor")
                tools[3]=False



    try:
        xbee=XBee()
    finally:
        if len(xbee.error_counts)>0:
            ins_error.append(xbee.error_log)
            if 5 in xbee.error_counts:
                ins_error_tool.append("xbee")
                tools[5]=False

    try:
        xcel = Xcel() #deleteの時に使う
    except RuntimeError:
        tools[6]=False #ここの部分は要検討

    def mxcel(data):
        #フェーズ、故障した部品、エラー分
        xcel_log = [11,None,[],None] #raspyのみ書く
        try:
            xcel.main(data)
        except RuntimeError:
            tools[6]=False
            import sys
            sys.exit(1)
        finally:
            if len(xbee.error_counts):
                xcel_log[2]=mget_time()
                xcel_log[-1]=xbee.error_log
                if 5 in xbee.error_counts:
                    xcel_log[-2].append("xcel")
                xbee.xbee_send(xcel_log)

    def mxcel(data):
        #フェーズ、故障した部品、エラー分
        xcel_log = [11,None,[],None] #raspyのみ書く
        try:
            xcel.main(data)
        except RuntimeError:
            tools[6]=False
            import sys
            sys.exit(1)
        finally:
            if len(xbee.error_counts):
                xcel_log[2]=mget_time()
                xcel_log[-1]=xbee.error_log
                if 5 in xbee.error_counts:
                    xcel_log[-2].append("xcel")
                xbee.xbee_send(xcel_log)

    def mxbee_send(data):
        #フェーズ、故障した部品、エラー分
        xbee_log = [12,None,[],None] #raspyのみ書く
        try:
            xbee.xbee_send(data)
        except RuntimeError:
            tools[5]=False
            import sys
            sys.exit(1)
        finally:
            if len(xbee.error_counts):
                xbee_log[2]=mget_time()
                xbee_log[-1]=xbee.error_log
                if 5 in xbee.error_counts:
                    xbee_log[-2].append("xbee")
                mxcel(xbee_log)  

    def rog(log):
        if tools[5] and tools[6]:
            mxbee_send(log)
            mxcel(log)
        elif tools[5]:
            mxbee_send(log)
        elif tools[6]:
            mxcel(log)
        else:
            pass  


    #ここで、ログを送信する
    ins_log=[1,mget_time(),tools[0],tools[1],tools[2],tools[3],tools[4],tools[5],tools[6],ins_error_tool,ins_error]
    rog(ins_log)       

    if False in tools:
        import sys
        sys.exit(1)


    def nlog(ward):
        notice_log=[9,ward]
        mxbee_send(notice_log)
        mxcel(notice_log)
      

    def mforward(wait_time):
        if wait_time>0:
            nlog(f"右モーターの正転、左モーターの逆転を{wait_time}秒間続けて、機体を前進させます。")
        else:
            nlog("右モーターの正転、左モーターの逆転をして、機体を前進させます。")
        #フェーズ、時間、故障した部品、エラー文      
        motor_log=[10,None,[],None]
        try:
            motors.forward()
            if wait_time>0:
                sleep(wait_time)
        except RuntimeError:
            tools[3]=False
            import sys
            sys.exit(1)
        finally:
            if len(motors.right_error_counts) or len(motors.left_error_counts):
                motor_log[1]=mget_time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                rog(motor_log)


    def mbackward(wait_time):
        if wait_time>0:
            nlog(f"右モーターの逆転、左モーターの正転を{wait_time}秒間続けて、機体を後進させます。")
        else:
            nlog("右モーターの逆転、左モーターの正転をして、機体を更新させます。")
        #フェーズ、時間、故障した部品、エラー文
        motor_log=[10,None,[],None]
        try:
            motors.backward()
            if wait_time>0:
                sleep(wait_time)
        except RuntimeError:
            tools[3]=False
            import sys
            sys.exit(1)
        finally:
            if len(motors.right_error_counts) or len(motors.left_error_counts):
                motor_log[1]=mget_time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                rog(motor_log)

    def mturn_left(wait_time):
        if wait_time>0:
            nlog(f"右モーターの正転、左モーターの正転を{wait_time}秒間続けて、機体を反時計回りに回転させます。")
        else:
            nlog("右モーターの正転、左モーターの正転をして、機体を反時計回りに回転させます。")
        #フェーズ、時間、故障した部品、エラー文
        motor_log=[10,None,[],None]
        try:
            motors.turn_left()
            if wait_time>0:
                sleep(wait_time)
        except RuntimeError:
            tools[3]=False
            import sys
            sys.exit(1)
        finally:
            if len(motors.right_error_counts) or len(motors.left_error_counts):
                motor_log[1]=mget_time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                rog(motor_log)


    def mturn_right(wait_time):
        if wait_time>0:
            nlog(f"右モーターの逆転、左モーターの逆転を{wait_time}秒間続けて、機体を時計回りに回転させます。")
        else:
            nlog("右モーターの逆転、左モーターの逆転を行います。")
        motor_log=[10,None,[],None]
        try:
            motors.turn_right()
            if wait_time>0:
                sleep(wait_time)
        except RuntimeError:
            tools[3]=False
            import sys
            sys.exit(1)
        finally:
            if len(motors.right_error_counts) or len(motors.left_error_counts):
                motor_log[1]=mget_time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                rog(motor_log)

    def mstop():
        motor_log=[10,None,[],None]
        try:
            motors.stop()
            nlog("モーターの回転を止めました。")
        except RuntimeError:
            tools[3]=False
            import sys
            sys.exit(1)
        finally:
            if len(motors.right_error_counts) or len(motors.left_error_counts):
                motor_log[1]=mget_time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                rog(motor_log)


    def mget_frame():
        try:
            frame=camera.get_frame()
            return frame       
        except RuntimeError:
            tools[2]=False
            import sys
            sys.exit(1)
        finally:
            if len(camera.error_counts):
                camera_log[-1]=camera.error_log
                if 5 in camera.error_counts:
                    camera_log[-2]="camera"
                    rog(camera_log)

    def mget_coordinate_xy(): #これはfeeds4の時に使う
        try:
            lat,lon=gps.get_coordinate_xy()
            return lat,lon
        except RuntimeError:
            tools[1]=False
            import sys
            sys.exit(1)
            
        finally:
            if len(gps.error_counts)>0:
                gps_log[-1]=gps.error_log
                if 5 in gps.error_counts:
                    gps_log[-2]="gps"
                    rog(gps_log)

    def m5get_coodinate_xy():
        #左からフェーズ、フェーズの分割番号、時間、緯度、経度,ゴールまでの距離、故障した部品、エラー文
        gps_log = [5,1,None,None,None,None,None,None]
        try:
            gps_log[2]=mget_time()
            lat,lon = gps.get_coordinate_xy()
            gps_log[3]=lat
            gps_log[4]=lon
            distance = get_distance(goal_lat, goal_lon, lat, lon)
            gps_log[5]=distance
            return lat,lon
        except RuntimeError:
            tools[1]=False
            import sys
            sys.exit(1)
        finally:
            if len(gps.error_counts):
                gps_log[7]=gps.error_log
                if 5 in gps.error_counts:
                    gps_log[6]="gps"  
            rog(gps_log)

    def m5get_dire_rot(pre_lat,pre_lon,now_lat,now_lon):
        #左からフェーズ、フェーズの分割番号、時間、進行方向、回転角度
        gps_log = [5,1,None,None,None,None]
        gps_log[2]=mget_time()
        move_direction = gps.move_direction(pre_lat,pre_lon,now_lat,now_lon)
        get_rotation_angle = get_rotation_angle(pre_lat,pre_lon,now_lat,now_lon,move_direction)   
        gps_log[3] = move_direction
        gps_log[4] = get_rotation_angle  
        mxbee_send(gps_log)
        mxcel(gps_log)
        return get_rotation_angle              

    nlog("カメラの確認を開始します")
    sleep(2)
    for i in range(10):
        # 左から、フェーズ、フェーズの中のフェーズ、時間、コーン検知、故障した部品、エラー文
        camera_log=[6,1,None,False,None,None]
        camera_log[2]=mget_time()
        frame=mget_frame()
        contour=find_cone(frame,lower_red1,upper_red1,lower_red2,upper_red2)
        if contour is not None:
            judge=judge_cone(contour,frame_area)
        else:
            judge=False
        
        if judge:
            camera_log[3]=True
            camera.cone_hozon(frame,contour)
        else:
            camera_log[3]=False
            camera.frame_hozon(frame)
        rog(camera_log)
        
    camera_log=[4,1,None,False,None,None]
    camera_log[2]=mget_time()
    frame=mget_frame()
    judge=find_parachute(frame,lower_yellow,upper_yellow,parea_threshold,center,frame_area,0)
    camera.parachute_hozon(frame)
    camera_log[3]=judge
    mxbee_send(camera_log)
    mxcel(camera_log)


    nlog("cdsの確認を開始します。")
    sleep(2)
    for i in range(10):
        #左から、フェーズ、時間、残り時間、明るさ、故障した部品、エラー文
        cds_log=[-1,None,None,"high",None,None]
        cds_log[1]=mget_time()
        try:
            cds.get_brightness()
            cds_log[2]=cds.brightness
        except:
            tools[0]=False
            import sys
            sys.exit(1)
        finally:
            if len(cds.error_counts):
                cds_log[4]=cds.error_log
                if 5 in cds.error_counts:
                    cds_log[3]="cds"          
            rog(cds_log)

        sleep(1)

    
    nlog("motorの確認を開始します")
    sleep(2)
    mforward(5)
    mturn_left(5)
    mturn_right(5)
    mbackward(5)
    mstop()
    sleep(2)
    
    nlog("servoの確認をします。")
    sleep(2)
    

    #変更点 
    try:            
        servo.rotate()
        
        start_time=time()
        while time()-start_time<srote_time:
            now_time=time()
            #左から、フェーズ、現在時間、残り時間
            wait_log=[8,None,None]
            jp_time=mget_time()
            wait_log[1]=jp_time
            wait_log[2]=int(srote_time-(now_time-start_time))
            #xbeeで送信
            mxbee_send(wait_log)
            mxcel(wait_log)
            keika=time()-now_time
            if keika<2:
                sleep(2-keika)
        
    except RuntimeError:
        nlog("サーボモーターが使えなくなったため、コードを停止します。")
        import sys
        sys.exit(1)
    finally:
        if len(servo.error_counts):
            #左から順にフェーズ、時間、故障した部品、エラー文
            servo_log=[-2,mget_time(),None,None]
            servo_log[3]=servo.error_log
            if 5 in servo.error_counts:
                servo_log[2]="servo"
            rog(servo_log)

    try:
        servo.stop()
    except RuntimeError:
        tools[0]=False
        import sys
        sys.exit(1)
    finally:
        if len(servo.error_counts):
            #左から順にフェーズ、時間、故障した部品、エラー文
            servo_log=[-2,mget_time(),None,None]
            servo_log[3]=servo.error_log
            if 5 in servo.error_counts:
                servo_log[2]="servo"
            rog(servo_log)


    nlog("GPSの確認を開始します。")
       
        

finally:        
    motors.release()
    gps.delete()
    camera.release()

    if False in tools:
        nlog("故障した部品があるため、ラズパイをシャットダウンさせます。")
        import os
        os.system("sudo shutdown now")
    else:
        nlog("全ての部品の確誋が終了しました。")
        nlog("待機モードに移ります。")