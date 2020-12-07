# -*- coding:utf8 -*-
from lib.struct.Point import Point


# 表示一个世界坐标
class WorldPoint(Point):

    def __init__(self, x, y):
        Point.__init__(self, x, y)

    # 将世界坐标转成地图坐标
    def to_map(self, area):
        from lib.struct.CoordiPoint import CoordiPoint
        zoneRange = self.getZoneRangeByZoneName(area)
        Y1 = zoneRange["Y1"]
        Y2 = zoneRange["Y2"]
        X1 = zoneRange["X1"]
        X2 = zoneRange["X2"]

        x = (self.x - X1) / (X2 - X1) * 100
        y = (self.y - Y1) / (Y2 - Y1) * 100
        return CoordiPoint(x, y)
