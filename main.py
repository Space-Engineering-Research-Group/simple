try:
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
    srote_time=60

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
    ldir_1=15
    ldir_2=14
    lPWM=18
    #機体の回転速度208度/s
    turn_speed=208
    #機体の前進速度20cm/s
    go_speed=20
    #９０度回転するときの待機時間
    sttime_90=90/turn_speed
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #以下の前進する距離はすべて単位がcm、角度の単位は度

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #フェーズ４＿３の時の角度のしきい値
    dire_threshold=5
    #フェーズ４＿1の時の進む距離を回転時間を定義
    go_dis_4_1=200
    go_time_4_1=go_dis_4_1/go_speed

    #フェーズ４＿４で前進するときの距離と回転時間を定義
    go_dis_4_4=200
    go_time_4_4=go_dis_4_4/go_speed

    #フェーズ5、前進するときの距離,回転角度と、回転時間を定義
    roteangle_5=90
    sttime_5=roteangle_5/turn_speed

    go_dis_5_2=200
    go_time_5_2=go_dis_5_2/go_speed

    go_dis_5_4=400
    go_time_5_4=go_dis_5_4/go_speed

    go_dis_5_5=500
    go_time_5_5=go_dis_5_5/go_speed


    #フェーズ６、kazu=1のときの回転角度と、回転時間を定義
    roteangle_6_1=60
    sttime_6_1=roteangle_6_1/turn_speed

    #フェーズ６，kazu=1で前進するときの距離と回転時間を定義
    go_dis6_1=100
    go_time_6_1=go_dis6_1/go_speed

    #フェーズ６，kazu=2の時の回転角度と、回転時間を定義
    roteangle_6_2=1
    sttime_6_2=roteangle_6_2/turn_speed

    #フェーズ６，kazu=2の時の前進する時間と回転角度を定義
    go_dis_far=100
    go_dis_close=2
    go_time_far=go_dis_far/go_speed
    go_time_close=go_dis_close/go_speed


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

    def mxbee_send(data):
        #フェーズ、故障した部品、エラー分
        xbee_log = [12,None,[],None] #raspyのみ書く
        try:
            xbee.xbee_send(data)
        except RuntimeError:
            tools[5]=False
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


    def nlog(ward):
        notice_log=[9,ward]
        rog(notice_log)
      

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
            raise RuntimeError
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
            raise RuntimeError
            
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
            raise RuntimeError
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
        rog(gps_log)
        return get_rotation_angle              



                    

    nlog("箱入れ待機時間")


    #箱に入れるまでの時間を仮に一分と置き、その間ずっと明るさを取得して、xbeeで送るようにする。

    if tools[0]==True:
        p=0
        while True:
            #左から、フェーズ、時間、明るさ、評価、故障した部品、エラー文
            fir_cds_log=[-1,None,None,"high",None,None]
            try:
                now_time=time()
                jp_time=mget_time()
                fir_cds_log[1]=jp_time
              
                cds.get_brightness()
                fir_cds_log[2]=cds.brightness
                if cds.brightness<=brightness_threshold:
                    fir_cds_log[3]="low"
                    p+=1
                else:
                    p=0
                if p==10:
                    nlog("箱に入ったことを認識しました。")
                    break
            except RuntimeError:
                tools[0]=False
                break
            finally:
                if len(cds.error_counts):
                    fir_cds_log[-1]=cds.error_log
                    if 5 in cds.error_counts:
                        fir_cds_log[-2]="cds"
                rog(cds.error_log)
            
            keika=time()-now_time
            if keika<2:
                sleep(2-keika)
    start_time=time()
    if tools[0]==True:
        nlog("cdsを用いた落下判定を開始します。")
        p=1
        while True:
            #左からフェーズ、時間、明るさ、明るさの評価、使えない部品、エラー文
            cds_log=[2,None,None,None,None,None]
            try:
                now_time=time()
                jp_time=mget_time()
                cds_log[1]=jp_time
                if now_time-start_time>=land_time:
                    land_judge=True
                    nlog("８分間一定以上の明るさを検知できなかったため、着地したと判定する。")
                    break
                cds.get_brightness()
                cds_log[2]=cds.brightness
                if cds.brightness >= brightness_threshold:
                    cds_log[3]=True
                    p+=1
                    rog(cds_log)
                else:
                    p=0
                
                if p==3:
                    fall_start_time=time()
                    nlog("一定以上の明るさを検知したため現在落下していると判定する。後１分経過したら着地したと判定")
                    while time()-fall_start_time<fall_time:
                        now_time=time()
                        #左からフェーズ、時間、残り時間
                        time_log=[8,None,None]
                        jp_time=mget_time()
                        time_log[1]=jp_time
                        time_log[2]=fall_time-(now_time-fall_start_time)
                        rog(time_log)
                        keika=time()-now_time
                        if keika<2:
                            sleep(2-keika)
                    nlog("１分経過したため着地したと判定")
                    break

            except RuntimeError :
                    tools[0]=False
                    break
            finally:
                if len(cds.error_counts):
                    cds_log[5]=cds.error_log
                    if 5 in cds.error_counts:
                        cds_log[4]="cds"
                rog(cds_log)

            keika=time()-now_time
            if keika<2:
                sleep(2-keika)
            
        
    if tools[0]==False:
        nlog("cdsが使えないため、起動してからの時間経過での着地判定に切り替えます。")
        while time()-start_time()<land_time:
            #左からフェーズ、時間、残り時間
            time_log=[8,None,None]
            now_time=time()
            jp_time=mget_time()
            time_log[1]=jp_time
            time_log[2]=land_time-(now_time-start_time)
            rog(time_log)
            keika=time()-now_time
            if keika<2:
                sleep(2-keika)
        nlog("起動から８分間経過したため、着地したとみなす。")
                
                
    if tools[4]==True:
        nlog("サーボモーターを用いてパラシュートの切り離しを行います。")
    else:
        nlog("サーボモーターが使えないため、コードを停止します。")      
        import sys
        sys.exit(1)

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
            rog(wait_log)
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
        pass
    finally:
        if len(servo.error_counts):
            #左から順にフェーズ、時間、故障した部品、エラー文
            servo_log=[-2,mget_time(),None,None]
            servo_log[3]=servo.error_log
            if 5 in servo.error_counts:
                servo_log[2]="servo"
            rog(servo_log)

    nlog("パラシュートの切り離しを行いました。")

    if tools[3]==False:
        nlog("モーターが使えないため処理を停止します")
        import sys
        sys.exit(1)

    if tools[2]==True and tools[1]==True:
        p=0
        try:
            
            nlog("現在地の緯度経度を取得")

            #左から、フェーズ、フェーズのフェーズ、時間、緯度、経度、故障した部品、エラー文
            gps_log=[4,2,None,None,None,None,None]
            gps_log[2]=mget_time()
            prelat,prelon=mget_coordinate_xy()
            gps_log[3]=prelat
            gps_log[4]=prelon
            rog(gps_log)
            nlog("パラシュートの検出を行う。")
            #左から、フェーズ、フェーズの中のフェーズ、時間、パラシュート検知、故障した部品、エラー文
            camera_log=[4,1,None,False,None,None]
            camera_log[2]=mget_time()
            frame=mget_frame()
            judge=find_parachute(frame,lower_yellow,upper_yellow,parea_threshold,center,frame_area,0)
            camera.parachute_hozon(frame)
            camera_log[3]=judge
            rog(camera_log)

            
            if judge==True:
                nlog("パラシュートを検知したため、機体を後進させ、GPSの位置情報から向いている向きを取得します。")
                mbackward(go_time_4_1)
            if judge==False:
                nlog("パラシュートを検知しなかったため、機体を前進させ、GPSの位置情報から向いている向きを取得します。")
                mforward(go_time_4_1)

            mstop()
                
            nlog("現在地の緯度経度を取得")
            
            #左から、フェーズ、フェーズのフェーズ、時間、緯度、経度、故障した部品、エラー文
            gps_log=[4,2,None,None,None,None,None]
            gps_log[2]=mget_time()
            nowlat,nowlon=mget_coordinate_xy()
            gps_log[3]=nowlat
            gps_log[4]=nowlon
            rog(gps_log)
            #変更点
            #左からフェーズ、フェーズの中のフェーズ、コーンに対する角度
            gps_log=[4,3,None]
            direction=gps.move_direction(prelat,prelon,nowlat,nowlon)
            gps_log[2]=direction
            rog(gps_log)
            #５度以上回転がずれてたら戻すようにしようと思う。（勘）
            sttime_4_3=abs(direction)/turn_speed
            if abs(direction)>dire_threshold:
                nlog("コーンに対する角度が５度より大きいため、回転してコーンと向き合うようにします。")
                if direction >dire_threshold:
                    mturn_right(sttime_4_3)
                else:
                    mturn_left(sttime_4_3)
            else:
                nlog("コーンに対する角度が５度以下なため、回転は行いません")    

                mstop()
                    
            nlog("パラシュートの検出を行います。")

            camera_log=[4,4,None,False,None,None,None]
            camera_log[2]=mget_time()
            frame=mget_frame()        
            sign,judge=find_parachute(frame,lower_yellow,upper_yellow,parea_threshold,center,frame_area,1) 
            camera.parachute_hozon(frame)
            camera_log[3]=judge
            camera_log[4]=sign
            rog(camera_log)

            if judge==True:
                print("パラシュートが検知されたため、回避を行います。")
                if sign==1:
                    nlog("パラシュートが機体に対して右側にあるため、左に回避します。")
                    mturn_left(sttime_90)
                    mforward(go_time_4_4)
                    mturn_right(sttime_90)
                else:
                    nlog("パラシュートが機体に対して左側にあるため、右に回避します。")
                    mturn_right(sttime_90)
                    mforward(go_time_4_4)
                    mturn_left(sttime_90)
            else:
                print("パラシュートが検知されなかったため、回避を行いません。")
            #１０は適当
            mforward(go_time_4_4)
            mstop()

        except RuntimeError:
            pass   

    #個々のロジック有用性確認済み。後はnlogの単体テストを行うだけで、ここは詳細テストはいらない。
    if tools[2]==False:
        if tools[1]==True:
            nlog("カメラが使えないので、パラシュートの回避を実行しません")
        else:
            nlog("カメラとgpsが使えないので、パラシュートの回避を実行しません")
    else:
        if tools[1]==False:
            nlog("gpsが使えないので、パラシュートの回避を実行しません")



    kazu=1
    gps_seikou=False
    cone_result=False
    while True:
        if tools[1] is False:
            if tools[2] is True:
                plan2="C"
                nlog("GPSが使えないため、プランcです。")
            else:
                plan2="D"
                nlog("カメラとGPS両方使えないため、プログラムを停止します。")
                import sys
                sys.exit(1)
        else:
            if tools[2] is False:
                plan2="B"
                nlog("カメラが使えないため、プランbです。")
        
    #gps


        if plan2 in ["A","B"]:
            try:
                while True:
                    #最初の緯度経度の取得は特別なので、関数化しない
                    #フェーズ、時間、緯度、経度,ゴールまでの距離,時間、進行方向、回転角度、故障した部品、エラー文
                    gps_log = [5,None,None,None,None,None,None,None,None,None,None]
                    try:
                        gps_log[1]=time()
                        pre_lat,pre_lon = gps.get_coordinate_xy()
                        gps_log[2]=pre_lat
                        gps_log[3]=pre_lon

                        distance=get_distance(pre_lat,pre_lon,goal_lat,goal_lon)

                        gps_log[4]=distance

                    except RuntimeError:
                        tools[1]=False
                        raise RuntimeError
                    finally:
                        if len(gps.error_counts):
                            gps_log[10]=gps.error_log
                            if 5 in gps.error_counts:
                                gps_log[9]="gps"  
                        rog(gps_log)


                        #初めからコーンが近い場合の処理     
                    distance=get_distance(pre_lat,pre_lon,goal_lat,goal_lon)

                    if plan2 == "A":
                        if distance<=A_x:
                            mforward(go_time_5_4)
                            mstop()
                            gps_seikou=True
                            nlog("始めからコーンが近いので成功")
                            break
                            
                        else:
                            nlog("コーンが遠いので前進")
                            mforward(go_time_5_5)
                            mstop()      

                    stack_count = 0
                    p=0

                    #loop started
                    while True:
                        p+=1
                        now_lat,now_lon = m5get_coodinate_xy()   
                
                        distance = get_distance(now_lat, now_lon, pre_lat, pre_lon)    

                        if distance<=s_x:
                            #stuckした場合の処理
                            stack_count+=1
                            if stack_count==5:#必要に応じて増やす
                                print("スタック5回目なので強制終了")
                                import sys
                                sys.exit(1)

                            mbackward(go_time_5_4)
                            mstop()
                            mturn_left(sttime_90)  
                            mstop()
                            mforward(go_time_5_4)
                            mstop()  

                            now_lat,now_lon = m5get_coodinate_xy()

                        #judge
                        distance = get_distance(goal_lat, goal_lon, now_lat, now_lon)     
                        
                        
                        if distance<=A_x and distance>B_x:
                            nlog("距離が4m以内")
                            mforward(go_time_5_4)
                            mstop()
                            if plan2 == "A":
                                nlog('planAより成功')
                                gps_seikou=True
                                break
                            
                        if distance<=B_x and distance>s_x:
                            nlog("距離が2m以内")

                            if plan2 == "B": 
                                nlog("planBより以下を行う")
                                #カメラが壊れていた場合
                                #左からフェーズ、フェーズの分割番号、時間、緯度、経度,ゴールまでの距離、故障した部品、エラー文
                                try:
                                    gps_log = [5,1,None,None,None,None,None,None]
                            
                                    gps_log[2]=time()
                                    gps_B_lat = []
                                    gps_B_lon = []
                                
                                    for i in range(2):
                                        lat,lon = gps.get_coordinate_xy()
                                        gps_B_lat.append(lat)
                                        gps_B_lon.append(lon)
                                        sleep(0.1)

                                    gps_B_lat_ave = sum(gps_B_lat)/2
                                    gps_B_lon_ave = sum(gps_B_lon)/2   
                                    gps_log[3]=gps_B_lat_ave
                                    gps_log[4]=gps_B_lon_ave  #60回の平均

                                    distance = get_distance(gps_B_lat_ave,gps_B_lon_ave,goal_lat,goal_lon)
                                    gps_log[5] = distance

                                except Exception :
                                    tools[1]=False
                                finally:
                                    if len(gps.error_counts):
                                        gps_log[7]=gps.error_log
                                        if 5 in gps.error_counts:
                                            gps_log[6]="gps"  
                                    rog(gps_log) #変則的なのでエラーつける
                                    

                                if distance<=B_x2:#適当、必要に応じて変える
                                    nlog("しかも距離が0.5m以内なので成功")
                                    gps_seikou=True
                                    break
                                    #成功したことを送る

                                rotation_angle = m5get_dire_rot(gps_B_lat_ave,gps_B_lon_ave,goal_lat,goal_lon) 
                                if rotation_angle > 0:
                                    mturn_right(rotation_angle/ turn_speed)  
                                else:
                                    z_rot = abs(rotation_angle)   
                                    mturn_left(z_rot/ turn_speed) 
                                mstop()
                                mforward(go_dis_5_2) #1/208の単位と、2m移動にかかる時間計算
                                mstop()
                                nlog("2m進んだので成功")
                                gps_seikou=True
                                break

                            else:#not B
                                nlog("planAより成功")
                                gps_seikou=True
                                break

                        #distanceが大きくてもまだ4m以上ある
                        rotation_angle = m5get_dire_rot(pre_lat,pre_lon,now_lat,now_lon)
                        if rotation_angle > 0:
                            mturn_right(rotation_angle/turn_speed)  
                        else:
                            z_rot = abs(rotation_angle)    
                            mturn_left(z_rot/turn_speed)

                        mstop()
                        mforward(go_dis_5_4)#この4秒は適当　あとで計算
                        mstop()
                        nlog("距離が4m以上。進んでやり直し")
                    break        
            
            except Exception :
                tools[1]=False
            finally:
                if len(gps.error_counts):
                    gps_log[7]=gps.error_log
                    if 5 in gps.error_counts:
                        gps_log[6]="gps"  
                mxbee_send(gps_log)
                mxcel(gps_log)   

        nlog("gps終了")        
        if plan2 == "B":
            break       
        



            #ここに、回転を行うコードを書く

        if plan2 in ["A","C"]:
            try:
                while True:
                    if kazu == 1:
                        p = 0
                        q = 0
                        while True:
                            nlog("コーンの検出を行う。")
                            # 左から、フェーズ、フェーズの中のフェーズ、時間、コーン検知、故障した部品、エラー文
                            camera_log = [6, 1, None, False, None, None]
                            camera_log[2] = mget_time()
                            frame = mget_frame()
                            contour = find_cone(frame, lower_red1, upper_red1, lower_red2, upper_red2)
                            if contour is not None:
                                judge = judge_cone(contour, frame_area)
                                camera_log[3] = judge
                            else:
                                judge = False
                            rog(camera_log)
                            if judge == True:
                                camera.cone_hozon(frame,contour)
                                kazu = 2   
                                break
                            if judge == False:
                                camera.frame_hozon(frame)
                                p += 1
                                nlog(f"コーンが見つからないため、機体を時計回りに回転させたのち、再び検出を行います。")
                                mturn_right(sttime_6_1)
                                mstop()
                                if p == int(360 / roteangle_6_1):
                                    q += 1
                                    if q == 5:
                                        nlog(f"{q}回してもコーンが検出されなかったので、不可能と判断して停止します。")
                                        tools[2]=False
                                        raise RuntimeError
                                    nlog("一周してもコーンが認識されないため、一度前進して動いてから、もう一度取得を始めます。")
                                    mforward(go_time_6_1)
                                    mstop()
                                    p = 0
                            

                    if kazu == 2:    
                        nlog("コーンが画面の中心にくるまでで回転しながら画像を取得します。")

                        while True:
                            sippai_6_2=0
                            for i in range(3):
                                #左から、フェーズ、フェーズのフェーズ、時間、コーン検出、コーンの位置判定、故障した部品、エラー文
                                camera_log=[6,2,None,False,None,None,None]
                                camera_log[2]=mget_time()
                                frame=mget_frame()
                                contour=find_cone(frame,lower_red1,upper_red1,lower_red2,upper_red2)
                                if contour is None:
                                    camera.frame_hozon(frame)
                                    rog(camera_log)
                                    nlog("コーンが検出出来なかったため、もう一度取得します。")
                                    sippai_6_2+=1

                                    continue
                                judge=judge_cone(contour,frame_area)
                                if judge==True:
                                    camera.cone_hozon(frame,contour)
                                    break
                                elif judge == False:
                                    camera.frame_hozon(frame)
                                    rog(camera_log)
                                    nlog("コーンが検出出来なかったため、もう一度取得します。")

                                    sippai_6_2+=1

                            if sippai_6_2==3:
                                nlog("三回コーンが検出できなかったため、もう一度回転してコーンを探します。")
                                kazu=1
                                break
                            camera_log[3]=True
                            sign=get_distance(contour,center)
                            camera_log[4]=sign
                            rog(camera_log)
                            if sign==0:
                                cone_result=to_stop(contour,frame_area)
                                if cone_result==True:
                                    kazu=3
                                    break
                                nlog("コーンが画面の中心にあるため、コーンに向かって前進をします。")
                                dis_judge=judge_cone(contour,frame_area,1)
                                if dis_judge==True:
                                    nlog("コーンが近くにあります。")
                                    mforward(go_time_close)
                                else:
                                    nlog("コーンが遠くにあります。")
                                    mforward(go_time_far)
                                mstop()
                            #ここの回転方向が正しいのかをしっかり確認するようにする。また、回転スピードなども考えるようにする。
                            elif sign==1:
                                nlog("コーンが中心の右側にあるため、時計回りの回転を行います。")
                                mturn_right(sttime_6_2)
                                mstop()
                                
                            else :
                                nlog("コーンが中心の左側にあるため、反時計回りの回転を行います。")
                                mturn_left(sttime_6_2)
                                mstop()
                            
                    if kazu==3:
                        #ここで終了したことを送る。
                        nlog("コーンに到着しました。")
                        break
            

            except RuntimeError as e:
                pass

        if cone_result:
            break
    #エラー起きてるけど、finallyとか使うのは確実なのでとりあえずつけとく
finally:        
    motors.release()
    gps.delete()
    camera.release()