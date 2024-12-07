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
    return rotation_angle