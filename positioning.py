import numpy as np

EARTH_RADIUS = 6_378_137.0   # meter

class GlobalCoord:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def to_relative(self, originGlobal):

        dLat = (self.lat - originGlobal.lat) * np.pi / 180
        dLng = (self.lng - originGlobal.lng) * np.pi / 180

        dNorth = dLat * EARTH_RADIUS
        dEast = dLng * EARTH_RADIUS * np.cos(originGlobal.lat * np.pi / 180)
        
        return RelativeCoord(originGlobal, dEast, dNorth)

    def __str__(self) -> str:
        return f"{[self.lng, self.lat]}"


class RelativeCoord:
    def __init__(self, originGlobal, x, y) -> None:
        self.x = x
        self.y = y
        self.originGlobal = originGlobal

    def to_global(self):
        dLat = self.y / EARTH_RADIUS
        dLon = self.x / (EARTH_RADIUS*np.cos(np.pi*self.originGlobal.lat/180))

        #New position in decimal degrees
        lat1 = self.originGlobal.lat + (dLat * 180/np.pi)
        lng1 = self.originGlobal.lng + (dLon * 180/np.pi)
        
        return GlobalCoord(lat1, lng1)

    def __str__(self) -> str:
        return f"{[self.x, self.y]}"