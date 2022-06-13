"""
This module contains helper functions for the main python script:

    * to_screen_coord - convert cartesian coord (origin at screen center) to pygame screen coordinate
    * to_cart_coord - convert pygame screen coordinate to cartesian coordinate (origin at screen center)
    * to_rad - convert degree to radian
    * to_deg - convert radian to degree
    * latlngToGlobalXY - convert latitude, longitude to global cartesian coordinate
    * globalXYTolatlng - convert global cartesian coordinate to latitude, longitude
    * calc_victim_pos - calculate the position of victim using triangulation
    * normalize_data - normalize data using min-max normalization
"""

import numpy as np

def to_screen_coord(
        cartPoint: tuple,
        screenSize: tuple = (600,600), zoom: int = 1
) -> tuple:
    """
    Converts a point in cartesian coordinate (origin at screen center)
    into pygame screen coordinate

    Parameters
    ----------
    cartPoint : tuple[int,int]
        X,Y cartesian coordinate pair to be converted
    screenSize : tuple[int,int], optional
        screen width, screen height pair for origin reference
        (default is (600,600))
    zoom : int, optional
        Specifies coordinate scaling (default is 1)

    Returns
    -------
    tuple
        X,Y pygame screen coordinate pair for the given cartesian coordinate
    """

    return (
        zoom*cartPoint[0] + screenSize[0]/2,
        screenSize[1]/2 - zoom*cartPoint[1]
    )


def to_cart_coord(
        screenPoint: tuple,
        screenSize: tuple = [600,600], zoom: int = 1
) -> tuple:
    """
    Converts a point in pygame screen coordinate into cartesian coordinate
    (origin at screen center)

    Parameters
    ----------
    screenPoint : tuple[int,int]
        X,Y pygame screen coordinate pair to be converted
    screenSize : tuple[int,int], optional
        screen width, screen height pair for origin reference
        (default is (600,600))
    zoom : int, optional
        Specifies coordinate scaling (default is 1)

    Returns
    -------
    tuple
        X,Y cartesian coordinate pair for the given pygame screen coordinate
    """

    return (
        zoom*screenPoint[0] - screenSize[0]/2,
        screenSize[1]/2 - zoom*screenPoint[1]
    )


def to_rad(deg: float) -> float:
    """
    Converts degree value into radian

    Parameters
    ----------
    deg : float
        degree value to be converted
    
    Returns
    -------
    float
        radian value for the given degree
    """

    return deg * np.pi / 180


def to_deg(rad: float) -> float:
    """
    Converts radian value into degree

    Parameters
    ----------
    rad : float
        radian value to be converted
    
    Returns
    -------
    float
        deg value for the given radian
    """

    return rad * 180 / np.pi


def latlngToGlobalXY(lat:float, lng:float) -> list:
    """
    Converts latitude and longitude value into global cartesian coordinate

    Parameters
    ----------
    lat, lng : float, float
        latitude and longitude value to be converted
    
    Returns
    -------
    list
        X,Y global cartesian coordinate for the given latitude, longitude
    """

    earthRadius = 6_378_160   # meter
    rad_lat = to_rad(lat)
    rad_lng = to_rad(lng)
    x = earthRadius * rad_lng * np.cos(rad_lat)
    y = earthRadius * rad_lat
    return [x, y]


def globalXYTolatlng(x:float, y:float) -> list:
    """
    Converts global cartesian coordinate value into latitude and longitude
    
    Parameters
    ----------
    x, y : float, float
        global cartesian coordinate value to be converted
    
    Returns
    -------
    float
        latitude, longitude for the given X,Y global cartesian coordinate
    """

    earthRadius = 6_378_160   # meter
    rad_lat = y / earthRadius
    rad_lng = x / earthRadius / np.cos(rad_lat)
    return [rad_lat, rad_lng]


def calc_victim_pos(posList:list, AoAList:list) -> list:
    """
    Calculate victim position (in latitude,longitude) for the given
    list of sampling position and AoA
    
    Parameters
    ----------
    posList : list
        List of sampling position (in latitude,longitude)
    AoAList : list
        List of AoA value at the sampling position (in degree)
    
    Returns
    -------
    list
        victim position (in latitude,longitude)

    Raises
    ------
    ValueError
        If position list and AoA list is not the same length
    """

    if len(posList) != len(AoAList): raise ValueError("Position list's and AoA list's length is not the same!")
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


def normalize_data(data: list) -> list:
    """
    Normalize the given data using min-max normalization
    
    Parameters
    ----------
    data : list
    
    Returns
    -------
    list
        The normalized data. If data is all 0, then it returns the data itself.
    """

    try:
        min_data, max_data = min(data), max(data)
        return [round((freq-min_data) / (max_data-min_data)) for freq in data]
    except ZeroDivisionError:
        return data


def color_text(text:str, color:str) -> str:
    if color == "black":
        return f"\u001b[30m{text}\u001b[0m"
    elif color == "red":
        return f"\u001b[31m{text}\u001b[0m"
    elif color == "green":
        return f"\u001b[32m{text}\u001b[0m"
    elif color == "yellow":
        return f"\u001b[33m{text}\u001b[0m"
    elif color == "blue":
        return f"\u001b[34m{text}\u001b[0m"
    elif color == "magenta":
        return f"\u001b[35m{text}\u001b[0m"
    elif color == "cyan":
        return f"\u001b[36m{text}\u001b[0m"
    elif color == "white":
        return f"\u001b[37m{text}\u001b[0m"
    else:
        return f"{text}"
