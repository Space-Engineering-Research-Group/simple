import os
import sys
sys.path.append(os.pardir)
from gps import *
from time import sleep,time
from motor import *
from xbee import *

#gps
gps = Gps()
xbee = Xbee()
motors = Motor()

plan2 = "A"
gps_seikou = False

goal_lat = 40
goal_lon = 40

tools=[True,True,True,True,True,True]

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
                xbee.xbee_send()

def m5get_coodinate_xy():
#左からフェーズ、フェーズの分割番号、時間、緯度、経度,ゴールまでの距離、故障した部品、エラー文
    gps_log = [5,1,None,None,None,None,None,None]
    try:
        gps_log[2]=time()
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
        xbee.xbee_send(gps_log)  

def m5get_dire_rot(pre_lat,pre_lon,now_lat,now_lon):
    #左からフェーズ、フェーズの分割番号、時間、進行方向、回転角度
    gps_log = [5,1,None,None,None,None]
    gps_log[2]=time()
    move_direction = gps.move_direction(pre_lat,pre_lon,now_lat,now_lon)
    get_rotation_angle = get_rotation_angle(pre_lat,pre_lon,now_lat,now_lon,move_direction)   
    gps_log[3] = move_direction
    gps_log[4] = get_rotation_angle 
    xbee.xbee_send(gps_log)   
    return get_rotation_angle              


def nlog(ward):
    notice_log=[9,ward]
    xbee.xbee_send(notice_log)


#main
if plan2 in ["A","B"]and gps_seikou==False:
    try:
        #最初の緯度経度の取得は特別なので、関数化しない
        #フェーズ、時間、緯度、経度,ゴールまでの距離,時間、進行方向、回転角度、故障した部品、エラー文
        gps_log = [5,None,None,None,None,None,None,None,None,None]
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
            xbee.xbee_send(gps_log)  


            #初めからコーンが近い場合の処理     
        distance=get_distance(pre_lat,pre_lon,goal_lat,goal_lon)
        if distance<4:
            mforward(20)
            mstop()
            gps_seikou=True
            
            
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
                        xbee.xbee_send(gps_log)  

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
        pass
