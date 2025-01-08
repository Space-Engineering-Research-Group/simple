try:
    from camera import *
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

    #箱の中に入れるまでの時間計測する。
    preparation_time=60
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
        servo=Servo(12,factory)
    except RuntimeError:
        tools[4]=False
    finally:
        if len(servo.error_counts)>0:
            ins_error.append(servo.error_log)
            if 5 in servo.error_counts:
                ins_error_tool.append("servo")
                tools[4]=False



    try:
        gps=Gps()
    finally:
        if len(gps.error_counts)>0:
            ins_error.append(gps.error_log)
            if 5 in gps.error_log:
               ins_error_tool.append("gps") 
               tools[1]=False

    gps_deta=[]
    #ここは大会の時に測る。
    goal_lat = 0
    goal_lon = 0

    width=640
    height=480
    fps=10
    center=width/2
    frame_area=width*height
    #カメラの画角（実験値）
    view_angle=120
    try:
        camera=Camera(width,height,fps)
    finally:
        if len(camera.error_counts)>0:
            ins_error.append(camera.error_log)
            if 5 in camera.error_counts:
                ins_error_tool.append("camera")
                tools[2]=False

    #ここの具体的な値はコーンの検査をして考える。
    lower_red1 = np.array([0, 100, 100])   # 下の範囲1 (0〜10度)
    upper_red1 = np.array([10, 255, 255])  # 上の範囲1
    lower_red2 = np.array([170, 100, 100]) # 下の範囲2 (170〜180度)
    upper_red2 = np.array([180, 255, 255]) # 上の範囲2

    #パラシュートの黄色をしっかり検出出来るようにする。
    lower_yellow=np.array([20, 100, 100])
    upper_yellow=np.array([40, 255, 255])


    #pin,pwmの値は決まった
    rdir_1=35
    rdir_2=37
    rPWM=33
    ldir_1=38
    ldir_2=40
    lPWM=36
    #機体の回転速度208度/s
    turn_speed=280
    motor_sttime=(view_angle/2)/turn_speed


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
        xbee=Xxbb()
    finally:
        if len(xbee.error_counts)>0:
            ins_error_tool.append("xbee")
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
                motor_log[2]=mget_time()
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
                motor_log[2]=mget_time()
                xbee_log[-1]=xbee.error_log
                if 5 in xbee.error_counts:
                    xbee_log[-2].append("xbee")
                mxcel(xbee_log)    


    #ここで、ログを送信する
    ins_log=[1,mget_time(),tools[0],tools[1],tools[2],tools[3],tools[4],tools[5],tools[6],ins_error_tool,ins_error]
    mxbee_send(ins_log)    
    mxcel(ins_log)     


    def nlog(ward):
        notice_log=[9,ward]
        mxbee_send(notice_log)
        mxcel(notice_log)
      

    def mforward(wait_time):
        if wait_time>0:
            nlog("右モーターの正転、左モーターの逆転を{wait_time}秒間続けて、機体を前進させます。")
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
                motor_log[2]=mget_time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                mxbee_send(motor_log)
                mxcel(motor_log)

    def mbackward(wait_time):
        if wait_time>0:
            nlog(f"右モーターの逆転、左モーターの正転を{wait_time}秒間続けて、機体を後進させます。")
        else:
            nlog("右モーターの逆転、左モーターの正転をして、機体を更新させます。")
        motor_log=[10,None,[],None]
        try:
            if wait_time>0:
                motors.backward()
            sleep(wait_time)
        except RuntimeError:
            tools[3]=False
            import sys
            sys.exit(1)
        finally:
            if len(motors.right_error_counts) or len(motors.left_error_counts):
                motor_log[2]=mget_time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                mxbee_send(motor_log)
                mxcel(motor_log)

    def mturn_left(wait_time):
        if wait_time>0:
            nlog(f"右モーターの正転、左モーターの逆転を{wait_time}秒間続けて、機体を反時計回りに回転させます。")
        else:
            nlog("右モーターの正転、左モーターの逆転をして、機体を反時計回りに回転させます。")
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
                motor_log[2]=mget_time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                mxbee_send(motor_log)
                mxcel(motor_log)


    def mturn_right(wait_time):
        if wait_time>0:
            nlog(f"右モーターの逆転、左モーターの逆転を{wait_time}秒間続けて、機体を時計回りに回転させます。")
        else:
            nlog(f"右モーターの逆転、左モーターの逆転を行います。")
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
                motor_log[2]=mget_time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                mxbee_send(motor_log)
                mxcel(motor_log)

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
                motor_log[2]=mget_time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                mxbee_send(motor_log)
                mxcel(motor_log)


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
                    mxbee_send(camera.error_log)
                    mxcel(camera.error_log)

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
                    mxbee_send(gps_log)
                    mxcel(gps_log)

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
            mxbee_send(gps_log)
            mxcel(gps_log)

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



                    

    nlog("箱入れ待機時間")
    start_time=time()


    #箱に入れるまでの時間を仮に一分と置き、その間ずっと明るさを取得して、xbeeで送るようにする。

    if tools[0]==True:
        while time()-start_time<preparation_time:
            #左から、フェーズ、時間、残り時間、明るさ、故障した部品、エラー文
            fir_cds_log=[-1,None,None,None,None,None]
            try:
                now_time=time()
                jp_time=mget_time()
                fir_cds_log[1]=jp_time
                fir_cds_log[2]=preparation_time-(now_time-start_time)
                cds.get_brightness()
                fir_cds_log[3]=cds.brightness
                    
            except RuntimeError:
                tools[0]=False
                break
            finally:
                if len(cds.error_counts):
                    fir_cds_log[5]=cds.log_errors
                    if 5 in cds.error_counts:
                        fir_cds_log[4]="cds"
                mxbee_send(cds.error_log)
                mxcel(cds.error_log)
            
            keika=time()-now_time
            if keika<2:
                sleep(2-keika)
    if tools[0]==False:
        nlog("cdsが使えないため、普通に待機します。")
        
        while time()-start_time<preparation_time:
            wait_log=[8,None,None]
            now_time=time()
            jp_time=mget_time()
            wait_log[1]=jp_time
            wait_log[2]=int(preparation_time-(now_time-start_time))
            #xbeeで送信
            mxbee_send(wait_log)
            mxcel(wait_log)
            sleep(5)

            



    #ここ変更点

    land_judge=False
    start_time=time()



    if tools[0]==True:
        
        while True:
            nlog("cdsを用いた落下判定を開始します。")
            #左からフェーズ、時間、明るさ、落下判断、使えない部品、エラー文
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
                if cds.brightness > brightness_threshold:
                    cds_log[3]=True
                    mxbee_send(cds_log)
                    mxcel(cds_log)

                    start_time=time()
                    nlog("一定以上の明るさを検知したため、１分経過したら着地したと判定")
                    while time()-start_time<fall_time:
                        #左からフェーズ、時間、残り時間
                        time_log=[8,None,None]
                        now_time=time()
                        jp_time=mget_time()
                        time_log[1]=jp_time
                        time_log[2]=fall_time-(now_time-start_time)
                        xbee.xbee_send(time_log)
                        mxbee_send(time_log)
                        mxcel(time_log)
                        sleep(2)

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
                mxbee_send(cds_log)
                mxcel(cds_log)
            
            keika=time()-cds_log[1]
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
        land_judge=True
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
        #個々の時間は後で計算する
        sleep(30)
        servo.stop()
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
            mxbee_send(servo_log)
            mxcel(servo_log)

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
            mxbee_send(gps_log)
            mxcel(gps_log)
            nlog("パラシュートの検出を行う。")
            #左から、フェーズ、フェーズの中のフェーズ、時間、パラシュート検知、故障した部品、エラー文
            camera_log=[4,1,None,False,None,None]
            camera_log[2]=mget_time()
            frame=mget_frame()
            judge=find_parachute(frame,lower_yellow,upper_yellow,center,0)
            camera_log[3]=judge
            mxbee_send(camera_log)
            mxcel(camera_log)

            if judge==True:
                nlog("パラシュートを検知したため、機体を後進させ、GPSの位置情報から向いている向きを取得します。")
                mbackward(10)
            if judge==False:
                nlog("パラシュートを検知しなかったため、機体を前進させ、GPSの位置情報から向いている向きを取得します。")

            mstop()
                
            nlog("現在地の緯度経度を取得")
            
            #左から、フェーズ、フェーズのフェーズ、時間、緯度、経度、故障した部品、エラー文
            gps_log=[4,2,None,None,None,None,None]
            gps_log[2]=mget_time()
            nowlat,nowlon=mget_coordinate_xy()
            gps_log[3]=nowlat
            gps_log[4]=nowlon
            mxbee_send(gps_log)
            mxcel(gps_log)
            #変更点
            #左からフェーズ、フェーズの中のフェーズ、コーンに対する角度
            gps_log=[4,3,None,None]
            direction=gps.move_direction(prelat,prelon,nowlat,nowlon)
            gps_log[2]=direction
            #５度以上回転がずれてたら戻すようにしようと思う。（勘）
            wait_time=abs(direction)/turn_speed
            if abs(direction)>5:
                if direction >5:
                    mturn_right(wait_time)
                else:
                    mturn_left(wait_time)
                

                mstop()
                    
            nlog("パラシュートの検出を行います。")
            frame=mget_frame()        
            sign,judge=find_parachute(frame,lower_yellow,upper_yellow,center,1)
                #左からフェーズ、時間、故障した部品、エラー文
            motor_log=[10,None,[],None]
                
            
            if judge==True:
                wait_time=90/turn_speed
                if sign==1:
                    mturn_left(wait_time)
                    mforward(10)
                    mturn_right(wait_time)
                else:
                    mturn_right(wait_time)
                    mforward(10)
                    mturn_left(wait_time)
                
                #１０は適当
                mforward(10)
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
            else:
                plan2="D"
                nlog("カメラとGPS両方使えないため、プログラムを停止します。")
                import sys
                sys.exit(1)
        else:
            if tools[2] is False:
                plan2="B"
        
        result=None
    #gps

        if plan2 in ["A","B"]and gps_seikou==False:
            try:
                #最初の緯度経度の取得は特別なので、関数化しない
                #フェーズ、時間、緯度、経度,ゴールまでの距離,時間、進行方向、回転角度、故障した部品、エラー文
                gps_log = [5,None,None,None,None,None,None,None,None,None]
                try:
                    gps_log[1]=time()
                    pre_lat,pre_lon = gps.get_coordinate_xy()
                    gps_log[2]=lat
                    gps_log[3]=lon

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
                    mxbee_send(gps_log)
                    mxcel(gps_log) 


                    #初めからコーンが近い場合の処理     
                distance=get_distance(pre_lat,pre_lon,goal_lat,goal_lon)
                if distance<4:
                    mforward(20)
                    mstop()
                    gps_seikou=True
                    continue
                   
                else:
                    mforward(30)
                    mstop()      

                stack_count = 0
                B_of_judge = 0

               #loop started
                while True:
                    now_lat,now_lon = m5get_coodinate_xy()   
            
                    distance = get_distance(now_lat, now_lon, pre_lat, pre_lon)            

                    if distance<1.4:
                        #stuckした場合の処理
                        stack_count+=1
                        if stack_count==4:
                            import sys
                            sys.exit(1)

                        mbackward(5)
                        mstop()
                        mturn_left(90/208)  
                        mstop()
                        mforward(5)
                        mstop()  

                        now_lat,now_lon = m5get_coodinate_xy()

                    #judge
                    distance = get_distance(goal_lat, goal_lon, now_lat, now_lon)            
                    
                    if B_of_judge == 0:
                        if distance<4:
                            mforward(20)
                            mstop()
                            if plan2 == "B":
                                B_of_judge = 1
                            gps_seikou=True
                            continue
                       
                    if distance<2:

                        if plan2 == "B": #planは適当あとで確認。
                            #カメラが壊れていた場合
                            #左からフェーズ、フェーズの分割番号、時間、緯度、経度,ゴールまでの距離、故障した部品、エラー文
                            gps_log = [5,1,None,None,None,None,None,None]
                            try:
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
                            except RuntimeError:
                                tools[1]=False
                                raise RuntimeError
                            finally:
                                if len(gps.error_counts):
                                    gps_log[7]=gps.error_log
                                    if 5 in gps.error_counts:
                                        gps_log[6]="gps"  
                                mxbee_send(gps_log)
                                mxcel(gps_log)

                            if distance<0.5:#適当
                                gps_seikou=True
                                #成功したことを送る

                            rotation_angle = m5get_dire_rot(gps_B_lat_ave,gps_B_lon_ave,goal_lat,goal_lon) 
                            if rotation_angle > 0:
                                mturn_right(rotation_angle/208)  
                            else:
                                z_rot = abc(rotation_angle)    
                                mturn_left(z_rot/208)
                            mstop()
                            mforward(4) #1/208の単位と、2m移動にかかる時間計算
                            mstop()

                        else:#not B
                            gps_seikou=True
                            continue

                    #distanceが大きくてもまだ4m以上ある
                    grotation_angle = m5get_dire_rot(pre_lat,pre_lon,now_lat,now_lon)
                    if rotation_angle > 0:
                        mturn_right(rotation_angle/208)  
                    else:
                        z_rot = abc(rotation_angle)    
                        mturn_left(z_rot/208)

                    mstop()
                    mforward(4)#この4秒は適当　あとで計算
                    mstop()
        
            
            except RuntimeError:
                continue

                


            #ここに、回転を行うコードを書く

        if plan2 in ["A","C"]:
            try:
                while True:
                    if kazu ==1:
                        p=0
                        q=-1
                        while True:
                            nlog("コーンの検出を行う。")
                            #左から、フェーズ、フェーズの中のフェーズ、時間、コーン検知、故障した部品、エラー文
                            camera_log=[6,1,None,False,None,None]
                            camera_log[2]=mget_time()
                            frame=mget_frame()
                            judge=find_cone(frame,lower_red1,upper_red1,lower_red2,upper_red2)
                            camera_log[3]=judge
                            mxbee_send(camera_log)
                            mxcel(camera_log)
                            if judge==True:
                                kazu=2
                                break
                            else:
                                p+=1
                                if p==int(360/(view_angle/2)):
                                    q+=1
                                    if q==3:
                                        nlog("３回動いてもコーンが検出されなかったので、不可能と判断して停止します。")
                                        import sys
                                        sys.exit(1)
                                    nlog("一周してもコーンが認識されないため、一度前進して動いてから、もう一度取得を始めます。")
                                    mforward(5)
                                    mstop()
                                    p=0
            
                        
                                nlog(f"パラシュートが見つからないため、機体を時計回りに回転させたのち、再び検出を行います。")
                                wait_time=(view_angle/2)/turn_speed
                                mturn_right(wait_time)
                                mstop()
                            

                    elif kazu == 2:
                        g=True #エラーって感じのところはgを使って抜け出すようにする。
                        
                        
                        while True:
                            nlog("コーンが画面の中心にくるまでで回転しながら画像を取得します。")

                            sign=-1
                            while sign!=0:
                                #左から、フェーズ、フェーズのフェーズ、時間、コーン検出、コーンの位置判定、故障した部品、エラー文
                                camera_log=[6,2,None,False,None,None,None]
                                camera_log[2]=mget_time()
                                frame=mget_frame()
                                contour=find_cone(frame,lower_red1,upper_red1,lower_red2,upper_red2)
                                if contour == None:
                                    nlog("コーンが検出出来ないため、もう一度回転して、コーン検出をはじめます。")
                                    g=False
                                    break
                                judge=judge_cone(contour,frame_area)
                                if judge == False:
                                    nlog("コーンが検出出来ないため、もう一度回転して、コーン検出をはじめます。")
                                    g=False
                                    mxbee_send(camera_log)
                                    mxcel(camera_log)
                                    break
                                camera_log[3]=True
                                sign=get_distance(contour,center)
                                camera_log[4]=sign
                                mxbee_send(camera_log)
                                mxcel(camera_log)
                                move_time=1/turn_speed
                                if sign==0:
                                    nlog("コーンが画面の中心にあるため、5秒間コーンに向かって前進をします。")
                                    mstop()
                                    break
                                #ここの回転方向が正しいのかをしっかり確認するようにする。また、回転スピードなども考えるようにする。
                                elif sign==1:
                                    nlog("コーンが中心の右側にあるため、時計回りの回転を行います。")
                                    mturn_right(move_time)
                                    
                                else :
                                    nlog("コーンが中心の左側にあるため、反時計回りの回転を行います。")
                                    mturn_left(move_time)
                                
                            if g == False:
                                kazu=1
                                break

                            motors.forward()  
                            start_time=time()
                            while time()-start_time<5:
                                #フェーズ、フェーズの中のフェーズ、時間、コーン検出、ゴール判定、故障した部品、エラー文
                                camera_log=[6,3,None,False,False,None,None]
                                now_time=time()
                                camera_log[2]=mget_time()
                                frame=mget_frame()
                                contour=find_cone(frame,lower_red1,upper_red1,lower_red2,lower_red2)
                                if contour == None:
                                    mxbee_send(camera_log)
                                    mxcel(camera_log)
                                    nlog("コーンが検出出来ないため、もう一度回転して、コーン検出をはじめます。")
                                    g=False
                                    break
                                judge=judge_cone(contour,frame_area)
                                if judge == False:
                                    mxbee_send(camera_log)
                                    mxcel(camera_log)
                                    nlog("コーンが検出出来ないため、もう一度回転して、コーン検出をはじめます。")
                                    g=False
                                    break

                                camera_log[3]=True

                                cone_result=to_stop(contour,frame_area)
                                camera_log[4]=cone_result
                                mxbee_send(camera_log)
                                mxcel(camera_log)
                                if cone_result:
                                    nlog("コーンに近づけたため、ゴール判定")
                                    break

                                #個々の秒数は適当
                                keika=time()-now_time
                                if keika<1:
                                    sleep(keika)
                                    
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
                pass

        if cone_result:
            break
    #エラー起きてるけど、finallyとか使うのは確実なのでとりあえずつけとく
finally:        
    motors.stop()
    gps.delete()
    camera.release()
    gps.delete()