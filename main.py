try:
    from .camera import *
    from .gps import *
    from .motor import *
    from time import sleep,time

    #ピンの具体的な値は後で決める
    forward_left_pin=1
    back_left_pin=1
    forward_right_pin=1
    back_right_pin=1
    motors=motor(forward_left_pin,back_left_pin,forward_right_pin,back_right_pin)
    gps=Gps()
    gps_deta=[]
    camera=Camera()
    width,height=camera.get_size()
    frame_area=width*height
    #ここの具体的な値はコーンの検査をして考える。大会前日とか？
    lower_red=[170,100,255]
    upper_red=[180,255,255]
    
    x=width/2


    #~~~センサ、サーボのコードは後で書く~~~#


    #パラシュートから逃げる
    motors.forward()
    sleep(2)
    motors.turn_left()
    i=0
    while True:
        i=i+1
        frame=camera.get_frame()
        contour=find_cone(frame,lower_red,upper_red)
        if len(contour):
            motors.stop()
            break
        if i==4:
            #エラーの発生のさせ方わからない
            raise 
        #モーターを９０度回転させるのに必要な秒数
        sleep(5)
    
    while True:
        gps.run_gps()
        gps_info=gps.get_coordinates()
        gps_deta.append(gps_info)

        frame=camera.get_frame()
        contour=find_cone(frame,lower_red,upper_red)
        sign=get_distance(contour,x)
        
        if sign==1:
            motors.turn_left()
        elif sign==-1:
            motors.turn_right()
         
        while sign!=0:
            frame=camera.get_frame()
            contour=find_cone(frame,lower_red,upper_red)
            sign=get_distance(contour,x)
            sleep(0.1)

        motors.forward()  
        start_time=time()
        while time()-start_time<5:
            frame=camera.get_frame()
            contour=find_cone(frame,lower_red,upper_red)
            result=to_stop(contour,frame_area)
            if result:
                print("コーンにたどり着きました")
                motors.stop()
                break
            sleep(1)
        


except:
    import sys
    print("Error:", sys.exc_info()[0])
    print(sys.exc_info()[1])
    import traceback
    print(traceback.format_tb(sys.exc_info()[2]))