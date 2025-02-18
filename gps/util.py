import math
from geopy.distance import distance
from geopy.distance import geodesic

def get_distance(goal_lat,goal_lon,latitude,longitude):

    
    pole_radius = 6356752.314245                  # 極半径
    equator_radius = 6378137.0                    # 赤道半径

     # 緯度経度をラジアンに変換
    glat = math.radians(goal_lat)
    glon = math.radians(goal_lon)
    nlat = math.radians(latitude)
    nlon = math.radians(longitude)

    lat_difference = glat - nlat       # 緯度差
    lon_difference = glon - nlon       # 経度差
    lat_average = (glat + glat) / 2    # 平均緯度

    e2 = (math.pow(equator_radius, 2) - math.pow(pole_radius, 2)) \
            / math.pow(equator_radius, 2)  # 第一離心率^2

    w = math.sqrt(1- e2 * math.pow(math.sin(lat_average), 2))

    m = equator_radius * (1 - e2) / math.pow(w, 3) # 子午線曲率半径

    n = equator_radius / w                         # 卯酉線曲半径

    distance = math.sqrt(math.pow(m * lat_difference, 2) \
                   + math.pow(n * lon_difference * math.cos(lat_average), 2)) # 距離計測
    return distance

def move_direction(past_lat, past_lon, now_lat, now_lon):
        past_lat, past_lon, now_lat, now_lon = map(math.radians, [past_lat, past_lon, now_lat, now_lon])
        delta_lon = now_lon - past_lon
        delta_lat = now_lat - past_lat
        bearing = math.atan2(delta_lon, delta_lat)
        bearing = math.degrees(bearing)  # ラジアンから度に変換

        return bearing 


def get_rotation_angle(goal_lat,goal_lon,latitude,longitude,move_direction): 
    #度をmに変換
    dlat = geodesic((latitude, longitude), (goal_lat, longitude)).meters  
    dlon = geodesic((latitude, longitude), (latitude, goal_lon)).meters
    print('できた')

    # 南北方向での符号を調整
    if goal_lat < latitude:
        dlat = -dlat
    
    # 東西方向での符号を調整
    if goal_lon < longitude:
        dlon = -dlon

    rotation_angle = math.degrees(math.atan2(dlon, dlat))
    if rotation_angle == None:
        print('None')

    rotation = rotation_angle - move_direction
    z_rot = abs(rotation)

    if z_rot <= 180 :
            return rotation
    else:
        if rotation >= 0:
            return rotation - 360
        else:
            return rotation + 360
       