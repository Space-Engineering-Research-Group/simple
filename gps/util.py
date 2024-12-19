import math
from geopy.distance import distance
from geopy.distance import geodesic

def get_distance(goal_lat,goal_lon,latitude,longitude):

    goal = (goal_lat,goal_lon)
    now = (latitude,longitude)
    distance = distance(goal,now).meters

    return distance

def get_rotation_angle(goal_lat,goal_lon,latitude,longitude,move_direction): 
    #度をmに変換
    dlat = geodesic((latitude, longitude), (goal_lat, longitude)).meters  
    dlon = geodesic((latitude, longitude), (latitude, goal_lon)).meters

    # 南北方向での符号を調整
    if goal_lat < latitude:
        dlat = -dlat
    
    # 東西方向での符号を調整
    if goal_lon < longitude:
        dlon = -dlon

    rotation_angle = math.degrees(math.atan2(dlon, dlat))

    rotation = rotation_angle - move_direction
    z_rot = math.abc(rotation)

    if z_rot <= 180 :
        if rotation >= 0:
            return rotation

    if z_rot >= 180 :
        if rotation >= 0:
            return rotation - 360
        else:
            return rotation + 360
        
def landing(grand,alt):
    #高度の誤差範囲
    a = 2
    dif = alt - grand
    if dif == a:
        return True
    else:
        return False      
            
