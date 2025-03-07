try:
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




    #このふぁいるは、エラーが出たら即死にしたいため、通常であればエラーを吐くようなところをsys.exit(1)としています。そこを覚えておいてください。

    #xbeeのエラーとかちゃんと追加してね


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    from gps import *
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


    try:
        xcel = Xcel() #deleteの時に使う
    except RuntimeError:
        tools[6]=False #ここの部分は要検討


    def mxcel(data):
        #フェーズ、故障した部品、エラー分
        xcel_log = [11,None,None] #raspyのみ書く
        try:
            xcel.xcel(data)
        except RuntimeError as e:
            tools[6]=False
            xcel_log[1]='csvファイル'
            xcel_log[2]=e
            print(f'xcel_error:{xcel_log}') 
         


    def rog(log):
        if tools[6]==True:
            mxcel(log)
        print(log)


    #ここで、ログを送信する
    ins_log=[1,mget_time(),tools[0],tools[1],tools[2],tools[3],tools[4],tools[5],tools[6],ins_error_tool,ins_error]
    rog(ins_log)       


    def nlog(ward):
        notice_log=[9,ward]
        rog(notice_log)


    nlog("GPSの確認を開始します。")
    while True:
        #左からフェーズ、フェーズの分割番号、時間、緯度、経度,ゴールまでの距離、故障した部品、エラー
        gps_log=[5,1,mget_time(),None,None,'なし',None,None]
        try:
            lat,lon = gps.get_xy_ceak()
            if lat != 0 and lon != 0:
                gps_log[3]=lat
                gps_log[4]=lon
                break
        except RuntimeError:
            tools[1]=False
            import sys
            sys.exit(1)
        finally:
            if len(gps.error_counts):
                if 5 in gps.error_counts:
                    gps_log[6]="gps" 
                rog(gps_log) 

    rog(gps_log)
    nlog('gps取得しました')
       

finally:        
    gps.delete()

    if False in tools:
        nlog("故障した部品があります。")
    else:
        nlog("全ての部品の確認が終了しました。") 
    