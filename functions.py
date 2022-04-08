import numpy as np

def to_screen_coord(
        cartPoint: tuple,
        screenSize: tuple = [600,600], zoom: int = 1
) -> tuple:
    return (
        zoom*cartPoint[0] + screenSize[0]/2,
        screenSize[1]/2 - zoom*cartPoint[1]
    )

def to_cart_coord(
        screenPoint: tuple,
        screenSize: tuple = [600,600], zoom: int = 1
) -> tuple:
    return (
        zoom*screenPoint[0] - screenSize[0]/2,
        screenSize[1]/2 - zoom*screenPoint[1]
    )

def to_rad(deg: float):
    return deg * np.pi / 180

def to_deg(rad: float):
    return rad * 180 / np.pi

def calc_detection_pattern(V, m):
    return np.dot(np.linalg.inv(V), m).astype(bool)

def calc_AoA(s, deltaTheta:float) -> float:
    sparsity = np.count_nonzero(s)
    the_list = np.transpose(s).tolist()
    if sparsity > 2: return None
    elif sparsity == 2:
        for i in range(len(the_list)):
            if [s[i-1], s[i]] == [True, True]:
                return ((i-1 % len(the_list)) + (i + 1)) * deltaTheta / 2
    elif sparsity == 1:
        i = the_list.index(True)
        return (i + i + 1) * deltaTheta / 2
    else: return None

def latlngToGlobalXY(lat:float, lng:float) -> list:
    earthRadius = 6_378_160   # meter
    rad_lat = to_rad(lat)
    rad_lng = to_rad(lng)
    x = earthRadius * rad_lng * np.cos(rad_lat)
    y = earthRadius * rad_lat
    return [x, y]

def globalXYTolatlng(x:float, y:float) -> list:
    earthRadius = 6_378_160   # meter
    rad_lat = y / earthRadius
    rad_lng = x / earthRadius / np.cos(rad_lat)
    return [rad_lat, rad_lng]

def calc_victim_pos(posList:list, AoAList:list) -> list:
    if len(posList) != len(AoAList): raise IndexError("Position list's and AoA list's length is not the same!")
    tmpA = []
    tmpb = []
    for i in range(len(posList)):
        x_i, y_i = latlngToGlobalXY(posList[i][0], posList[i][1])
        a_i = to_rad(AoAList[i])
        tan_a = np.tan(a_i)
        tmpA.append([-tan_a, 1])
        tmpb.append([y_i - x_i*tan_a])
    A = np.array(tmpA)
    # A = np.array(
    #     [[-tan(a1), 1],
    #      [-tan(a2), 1],
    #      [-tan(a3), 1]]
    # )
    b = np.array(tmpb)
    # b = np.array(
    #     [[y1-x1*tan(a1)],
    #      [y2-x2*tan(a2)],
    #      [y3-x3*tan(a3)]]
    # )

    # c = ( (A' * A)^-1 * A' * b )'
    targetPos = np.transpose(np.linalg.inv(np.transpose(A).dot(A)).dot(np.transpose(A)).dot(b) ).tolist()[0]

    return globalXYTolatlng(targetPos[0], targetPos[1])

def normalize_data(data):
    try:
        min_data, max_data = min(data), max(data)
        return [round((freq-min_data) / (max_data-min_data)) for freq in data]
    except ZeroDivisionError:
        return data