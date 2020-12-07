# -*- coding:utf8 -*-
from lib.base.Base import Base
from lib.db.sqlite3 import Sqlite3


# Point代表一个由x，y坐标确定的点，比如屏幕像素点或者人物坐标点
class Point(Base):
    x = 0
    y = 0

    def __init__(self, x, y):
        Base.__init__(self)
        self.x = x
        self.y = y

    def toString(self):
        return str(self.x) + ',' + str(self.y)

    # 根据地图名称获取地图的世界坐标范围
    def getZoneRangeByZoneName(self, name):
        ret = Sqlite3.query("select * from WorldMapArea where AreaName='" + name + "'", "one")
        if ret is None:
            raise Exception("地图名称未找到:" + name)
        return {"Y1": ret[3], "Y2": ret[4], "X1": ret[5], "X2": ret[6]}
