try:
    from cds import *
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



    try:
        xbee=Xxbb()
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
            import sys
            sys.exit(1)
        finally:
            if len(xbee.error_counts):
                xbee_log[2]=mget_time()
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

    nlog("明るさの取得を始めます。")

    p=0
    while True:
        now_time=time()
        #左からフェーズ、時間、明るさ、故障した部品、エラー文
        cds_log=[2,None,None,None,None,None]
        cds_log[1]=mget_time()
        try:
            cds.get_brightness()
            cds_log[2]=cds.brightness
            if cds.brightness<brightness_threshold:
                p+=1
            else:
                p=0
            if p==10:
                nlog("２０秒間連続で暗くなっていることを確認しました。")
                import sys
                sys.exit(1)
        except:
            tools[0]=False
            import sys
            sys.exit(1)
        finally:
            if len(cds.error_counts):
                cds_log[4]=cds.error_log
                if 5 in cds.error_counts:
                    cds_log[3]="cds"          
                mxbee_send(cds_log)
                mxcel(cds_log)

        keika=time()-now_time
        if keika<2:
            sleep(2-keika)
        


finally:
    if False in tools:
        nlog("部品が使えてないのでラズパイをシャットダウンします。")
        import os
        os.system("sudo shutdown now")
    else:
        nlog("本番用コードに移ります。")