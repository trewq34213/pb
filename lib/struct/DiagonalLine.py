# -*- coding:utf8 -*-
from lib.struct.Point import Point
from lib.struct.CoordiPoint import CoordiPoint
from lib.base.Base import Base
from lib.struct.Line import Line


# 表示区域的对角线
class DiagonalLine(Base):
    def __init__(self, area, i=1):
        super().__init__()
        self.line1 = Line(Point(area["leftTop"][0], area["leftTop"][1]), Point(area["rightBottom"][0], area["rightBottom"][1]))
        self.line2 = Line(Point(area["leftBottom"][0], area["leftBottom"][1]), Point(area["rightTop"][0], area["rightTop"][1]))
        self.area = area
        self.i = i

    # 获取线段中点
    def get_center_ponit(self):
        if self.i == 1:
            return Point((self.line1.start.x + self.line1.end.x) / 2, (self.line1.start.y + self.line1.end.y) / 2)
        else:
            return Point((self.line2.start.x + self.line2.end.x) / 2, (self.line2.start.y + self.line2.end.y) / 2)

    # 获取线段长度
    def get_len(self):
        if self.i == 1:
            return round(((self.line1.start.x - self.line1.end.x) ** 2 + (self.line1.start.y - self.line1.end.y) ** 2) ** 0.5, 8)
        else:
            return round(((self.line2.start.x - self.line2.end.x) ** 2 + (self.line2.start.y - self.line2.end.y) ** 2) ** 0.5, 8)

    # 将线段等分，返回各分的坐标
    def divide_line(self, cut):
        if self.i == 1:
            if cut <= 1:
                return [self.line1.start, self.line1.end]
            ret = []
            for i in range(cut):
                x = self.line1.start.x + (self.line1.end.x - self.line1.start.x) / cut * i
                y = self.line1.start.y + (self.line1.end.y - self.line1.start.y) / cut * i
                ret.append(Point(x, y))
            return ret
        else:
            if cut <= 1:
                return [self.line2.start, self.line2.end]
            ret = []
            for i in range(cut):
                x = self.line2.start.x + (self.line2.end.x - self.line2.start.x) / cut * i
                y = self.line2.start.y + (self.line1.end.y - self.line2.start.y) / cut * i
                ret.append(Point(x, y))
            return ret

    # 获取下一个线段上的点
    def get_next_point(self, nowPos, cut):
        from lib.navigation.AreaFighting import AreaFighting
        from lib.navigation.NvBase import NvBase
        if not AreaFighting.pos_in_area(nowPos, self.area):
            return False
        all = self.divide_line(cut)
        near = NvBase().getNearstPoint(nowPos, all)
        return CoordiPoint(near.x, near.y)

    # 切换对角线
    def switch_line(self):
        if self.i == 1:
            self.i = 2
        else:
            self.i = 1
        return self
