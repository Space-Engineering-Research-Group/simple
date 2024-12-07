import math
def get_distance(goal_lat,goal_lon,latitude,longitude):

    dlat = goal_lat - latitude
    dlon = goal_lon - longitude
    distance = math.sqrt(dlat ** 2 + dlon ** 2)
    
    return distance

def get_rotation_angle(goal_lat,goal_lon,latitude,longitude,move_direction): 
    
    dlat = goal_lat - latitude
    dlon = goal_lon - longitude

    rotation_angle = math.degrees(math.atan2(dlon, dlat))

    rotation = rotation_angle - move_direction
    z_rot = math.abc(rotation)

    if z_rot <= 180 :
        if rotation >= 0:
            return rotation
        else:
            return rotation
        
    if z_rot >= 180 :
        if rotation >= 0:
            return rotation - 360
        else:
            return rotation + 360
