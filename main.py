try:
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
    #カメラの画角（仮定）
    view_angle=70
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

    def mforward(wait_time):
        if wait_time>0:
            nlog("右モーターの正転、左モーターの逆転を{wait_time}秒間続けて、機体を前進させます。")
        else:
            nlog("右モーターの正転、左モーターの逆転をして、機体を前進させます。")
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
                motor_log[2]=time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                xbee.xbee_send(motor_log)

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
                motor_log[2]=time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                xbee.xbee_send(motor_log)

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
                motor_log[2]=time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                xbee.xbee_send(motor_log)


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
                motor_log[2]=time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                xbee.xbee_send(motor_log)

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
                motor_log[2]=time()
                motor_log[-1]=motors.error_log
                if 5 in motors.right_error_counts:
                    motor_log[-2].append("right motor")
                if 5 in motors.left_error_counts:
                    motor_log[-2].append("left motor")
                xbee.xbee_send(motor_log)


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
                    xbee.xbee_send(camera.error_log)

    def mget_coordinate_xy():
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
                    xbee.xbee_send()

    def nlog(ward):
        notice_log=[9,ward]
        xbee.xbee_send(notice_log)
                    


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
            nlog("cdsが使えないため、起動してからの時間経過での着地判定に切り替えます。")

        if plan1 =="A":
            try:
                while land_judge==False:
                    nlog("cdsを用いた落下判定を開始します。")
                    #左からフェーズ、プラン、時間、明るさ、落下判断、使えない部品、エラー文
                    cds_log=[2,"A",0,None,None,None,None]
                    try:
                        cds_log[1]=time()
                        if cds_log[1]-start_time>land_time:
                            land_judge=True
                            nlog("８分間一定以上の明るさを検知できなかったため、着地したと判定する。")
                            continue
                        cds.get_brightness()
                        cds_log[4]=cds.brightness
                        if cds.brightness < brightness_threshold:
                            cds_log[3]=True
                            start_time=time()
                            nlog("一定以上の明るさを検知したため、１分経過したら着地したと判定")
                            while time()-start_time<fall_time:
                                #左からフェーズ、時間、残り時間
                                time_log=[8,None,None]
                                now_time=time()
                                time_log[1]=now_time
                                time_log[2]=fall_time-(now_time-start_time)
                                xbee.xbee_send(time_log)
                            nlog("１分経過したため着地したと判定")
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
            nlog("起動から８分間経過したため、着地したとみなす。")
                
                
    if tools[4]==True:
        nlog("サーボモーターを用いてパラシュートの切り離しを行います。")
    else:
        nlog("サーボモーターが使えないため、コードを停止します。")      
        import sys
        sys.exit(1)

    try:            
        servo.rotate()
        #個々の時間は後で計算する
        sleep(30)
    except RuntimeError:
        nlog("サーボモーターが使えなくなったため、コードを停止します。")
        import sys
        sys.exit(1)

    nlog("パラシュートの切り離しを行いました。")

    if tools[2]==True:
        p=0
        try:
            while True:
                nlog("パラシュートの検出を行う。")
                #左から、フェーズ、フェーズの中のフェーズ、時間、パラシュート検知、故障した部品、エラー文
                camera_log=[4,1,None,False,None,None]
                camera_log[2]=time()
                frame=mget_frame()
                judge=find_parachute(frame,lower_yellow,upper_yellow,center,0)
                camera[3]=judge
                #左からフェーズ、時間、故障した部品、エラー文
                motor_log=[10,None,[],None]
                if judge==True:
                    nlog("パラシュートを検知したため、機体を後進させ、GPSの位置情報から向いている向きを取得します。")

                    nlog("現在地の緯度経度を取得")

                    #左から、フェーズ、フェーズのフェーズ、時間、緯度、経度、故障した部品、エラー文
                    gps_log=[4,2,None,None,None,None,None]
                    gps_log[2]=time()
                    prelat,prelon=mget_coordinate_xy()
                    gps_log[3]=prelat
                    gps_log[4]=prelon
                    xbee.xbee_send(gps_log)

                    #10は割とマジで適当
                    mbackward(10)

                    mstop()
                    
                    nlog("現在地の緯度経度を取得")
                    
                    #左から、フェーズ、フェーズのフェーズ、時間、緯度、経度、故障した部品、エラー文
                    gps_log=[4,2,None,None,None,None,None]
                    gps_log[2]=time()
                    nowlat,nowlon=mget_coordinate_xy()
                    gps_log[3]=nowlat
                    gps_log[4]=nowlon
                    xbee.xbee_send(gps_log)
                    #左からフェーズ、フェーズの中のフェーズ、コーンに対する角度、故障した部品、エラー文
                    gps_log=[4,3,None,None,None]
                    direction=gps.move_direction(prelat,prelon,nowlat,nowlon)
                    gps_log[2]=direction
                    #５度以上回転がずれてたら戻すようにしようと思う。（勘）
                    wait_time=abs(direction)/turn_speed
                    if direction>5 or direction<-5:
                        if direction >5:
                            mturn_right(wait_time)
                        else:
                            mturn_left(wait_time)
                        

                        mstop()
                    
                    break
                else:
                    p+=1

                    if p==int(360/(view_angle/2)):
                        nlog("パラシュートが認識されないため、回避をせず、次の動作へ移ります。")
                        #めんどくさいのでエラーを発生させて個々の部分の処理を終了する。これは、決して問題が起きたとかではなく、ただ単にめんどくさいのでエラーを吐くだけである。
                        raise RuntimeError
                    
                    nlog(f"パラシュートが見つからないため、機体を時計回りに回転させたのち、再び検出を行います。")
                    wait_time=(view_angle/2)/turn_speed
                    mturn_right(wait_time)
                    mstop()
                    
                
            
            nlog("パラシュートの検出を行います。")
            frame=mget_frame()        
            sign,judge=find_parachute(frame,lower_yellow,upper_yellow,center,1)
                #左からフェーズ、時間、故障した部品、エラー文
            motor_log=[10,None,[],None]
            if judge==False:
                sign=-1
                #画角が１８０度以内である前提
                wait_time=(90-(view_angle/2))/turn_speed
                nlog("パラシュートが見つからないため、機体を反時計回りに回転させたのち、再度検出を行います。")
                mturn_left(wait_time)
                mstop()
                nlog("パラシュートの検出を行います。")
                frame=mget_frame()
                judge=find_parachute(frame,lower_yellow,upper_yellow,center,0)
                if judge==False:
                    nlog("パラシュートのが見つからないため、機体を時計回りに回転させたのち、再度検出を行う。")
                    sign=1
                    wait_time=2*wait_time
                    mturn_right(wait_time)
                    mstop()
                    frame=mget_frame()
                    judge=find_parachute(frame,lower_yellow,upper_yellow,center,0)
                    nlog("機体とコーンを正対させます。")
                    wait_time=wait_time/2
                    mturn_left(wait_time)
                    mstop()
            
            if judge==True:
                wait_time=90/turn_speed
                if sign==1:
                    mturn_left()
                    sleep(wait_time)
                    mturn_right()
                    sleep(wait_time)
                    mstop()
                else:
                    mturn_right()
                    sleep(wait_time)
                    mturn_left()
                    sleep(wait_time)
                    mstop()

            
            #１０秒は適当
            mforward(10)




        except RuntimeError:
            pass   

    if tools[2]==False:
        nlog("カメラが使えないので、パラシュートの回避を実行しません")



    kazu=1
    gps_seikou=False
    cone_result=False
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

        if plan3 in ["A","C"]:
            try:
                while True:
                    if kazu ==1:
                        p=0
                        q=0
                        while True:
                            nlog("コーンの検出を行う。")
                            #左から、フェーズ、フェーズの中のフェーズ、時間、コーン検知、故障した部品、エラー文
                            camera_log=[6,1,None,False,None,None]
                            camera_log[2]=time()
                            frame=mget_frame()
                            judge=find_cone(frame,lower_red1,upper_red1,lower_red2,upper_red2)
                            camera[3]=judge
                            xbee.xbee_send(camera_log)
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
                                camera_log[2]=time()
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
                                    xbee.xbee_send(camera_log)
                                    break
                                camera_log[3]=True
                                sign=get_distance(contour,center)
                                camera_log[4]=sign
                                if sign==0:
                                    nlog("コーンが画面の中心にあるため、5秒間コーンに向かって前進をします。")
                                    mstop()
                                    break
                                #ここの回転方向が正しいのかをしっかり確認するようにする。また、回転スピードなども考えるようにする。
                                elif sign==1:
                                    nlog("コーンが中心の右側にあるため、回転を続けます。")
                                    mturn_right(-1)
                                    
                                else :
                                    nlog("コーンが中心の左側にあるため、回転を続けます。")
                                    mturn_left(-1)
                                
                            if g == False:
                                kazu=1
                                break

                            motors.forward()  
                            start_time=time()
                            while time()-start_time<5:
                                #フェーズ、フェーズの中のフェーズ、時間、コーン検出、ゴール判定、故障した部品、エラー文
                                camera_log=[6,3,None,False,False,None,None]
                                camera_log[2]=time()
                                frame=mget_frame()
                                contour=find_cone(frame,lower_red1,upper_red1,lower_red2,lower_red2)
                                if contour == None:
                                    nlog("コーンが検出出来ないため、もう一度回転して、コーン検出をはじめます。")
                                    xbee.xbee_send(camera_log)
                                    g=False
                                    break
                                judge=judge_cone(contour,frame_area)
                                if judge == False:
                                    nlog("コーンが検出出来ないため、もう一度回転して、コーン検出をはじめます。")
                                    xbee.xbee_send(camera_log)
                                    g=False
                                    break

                                camera_log[3]=True

                                cone_result=to_stop(contour,frame_area)
                                camera_log[4]=cone_result
                                if cone_result:
                                    nlog("コーンに近づけたため、ゴール判定")
                                    break
                                #個々の秒数は適当
                                sleep(0.5)
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
    gps.run_gps()
    camera.release()
    gps.delete()

