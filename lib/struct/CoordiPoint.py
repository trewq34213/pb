# -*- coding:utf8 -*-
from lib.struct.Point import Point


# 表示一个游戏内坐标
class CoordiPoint(Point):
    def __init__(self, x, y):
        Point.__init__(self, x, y)

    # 将地图坐标转成世界坐标
    def to_world(self, area):
        from lib.struct.WorldPoint import WorldPoint
        zoneRange = self.getZoneRangeByZoneName(area)
        Y1 = zoneRange["Y1"]
        Y2 = zoneRange["Y2"]
        X1 = zoneRange["X1"]
        X2 = zoneRange["X2"]

        ret = []
        # 世界坐标的x需要用地图坐标的y来变换，世界坐标的y需要用地图坐标的x来变换，因为世界坐标的x是地图坐标的y，世界坐标的y是地图坐标的x
        ret.append(WorldPoint(self.y / 100 * (X2 - X1) + X1, self.x / 100 * (Y2 - Y1) + Y1))
        # ret.append(WorldPoint(-coordi.y / 100 * (X2 - X1) + X1,coordi.x / 100 * (Y2 - Y1) + Y1))
        # ret.append(WorldPoint(coordi.y / 100 * (X2 - X1) + X1,-coordi.x / 100 * (Y2 - Y1) + Y1))
        # ret.append(WorldPoint(-coordi.y / 100 * (X2 - X1) + X1,-coordi.x / 100 * (Y2 - Y1) + Y1))

        # 因为正负号丢失的关系，可能得到4个世界坐标，得找出正确的那个
        realWorlds = []
        for w in ret:
            if min(X1, X2) <= w.x <= max(X1, X2) and min(Y1, Y2) <= w.y <= max(Y1, Y2):
                realWorlds.append(w)

        if len(realWorlds) == 1:
            return realWorlds[0]
        raise Exception(self.toString() + ":无法转换为世界坐标")
