try:
    from .camera import *
    from .gps import *
    from .motor import *
    from .cds import *
    from .servo import *
    from time import sleep,time
    from csv  import writer

    cds=Cds()
    #明るさの閾値は曇りの日に明るさを取得して決める
    brightness_threshold=0.3
    #ピンの値は回路班が後で決めるので仮の値
    servo=Servo(12)
    gps=Gps()
    gps_deta=[]
    camera=Camera()
    width,height=camera.get_size()
    frame_area=width*height
    #ここの具体的な値はコーンの検査をして考える。大会前日とか？
    lower_red=[170,100,255]
    upper_red=[180,255,255]
    
    x=width/2

    #pin,pwmの値は決まった
    rdir_1=35
    rdir_2=37
    rPWM=33
    ldir_1=38
    ldir_2=40
    lPWM=36
    motors=Motor(rdir_1,rdir_2,rPWM,ldir_1,ldir_2,lPWM)


    while True:
        bright=cds.get_brightness()
        if bright > brightness_threshold:
            break

        sleep(2)
    
    #明るさを検知してから１０秒後にサーボを回す
    #この１０秒は仮の値である
    sleep(10)
    servo.rotate()
    sleep(2)


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
            motors.stop()
            print("コーンが見つかりません")
            import sys
            sys.exit()            
        #モーターを９０度回転させるのに必要な秒数
        sleep(5)
    i=False
    while True:
        gps.run_gps()

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
                i=True
                break
            sleep(1)
        if i:
            break
        
    gps.run_gps()

except:
    import sys
    print("Error:", sys.exc_info()[0])
    print(sys.exc_info()[1])
    import traceback
    print(traceback.format_tb(sys.exc_info()[2]))

finally:
    camera.release()
    gps.delete()   