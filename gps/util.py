import math
def get_distance(latitude,longitude):
    #ゴールの座標当日わかる
    goal_lat=  x
    goal_lon=  y

    dlat = goal_lat - latitude
    dlon = goal_lon - longitude
    distance = math.sqrt(dlat ** 2 + dlon ** 2)
    
    return distance

def get_rotation_angle(latitude,longitude,move_direction): 
    #ゴールの座標当日わかる
    goal_lat=  x
    goal_lon=  y

    dlat = goal_lat - latitude
    dlon = goal_lon - longitude

    angle = math.degrees(math.atan2(dlon, dlat))
    rotation_angle = 180 - abs(angle)

    return rotation_angle