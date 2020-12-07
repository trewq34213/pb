# -*- coding:utf8 -*-
import math
from lib.unit.Target import Target
from lib.pixel.PixelData import PixelData
from lib.struct.CoordiPoint import CoordiPoint


# 代表一个小队队友
class Party(Target):
    i = 1  # 第几个队友

    def __init__(self, i):
        Target.__init__(self)
        if i < 1 or i > 4:
            raise Exception("队友只能是1-4")
        self.i = i
        self.rang = self.__get_party_slots()

    # 获取生命百分比
    def getLiftPercent(self):
        point = PixelData.getPointByIndex(self.rang["start"] + 4)
        rgb = self.get_color_RGB(point.x, point.y)
        return rgb[0]

    # 获取魔法（怒气）百分比
    def getManaPercent(self):
        point = PixelData.getPointByIndex(self.rang["start"] + 4)
        rgb = self.get_color_RGB(point.x, point.y)
        return rgb[1]

    # 获取坐标
    def getCoordi(self):
        xPoint = PixelData.getPointByIndex(self.rang['start'])
        yPoint = PixelData.getPointByIndex(self.rang['start'] + 1)
        x = xPoint.getFloat(10000)
        y = yPoint.getFloat(10000)
        return CoordiPoint(x, y)

    # 获取尸体坐标，返回0,0表示没有死
    def getCropsCoordi(self):
        xPoint = PixelData.getPointByIndex(self.rang['start'] + 2)
        yPoint = PixelData.getPointByIndex(self.rang['start'] + 3)
        x = xPoint.getFloat(10000)
        y = yPoint.getFloat(10000)
        return CoordiPoint(x, y)

    # 获取各种状态
    def getStatus(self):
        bools = PixelData.get_point_bools(self.rang['start'] + 5, 23)
        return {"combat": bools[0], "dead": bools[1]}

    # 获取玩家和队友之间的距离
    def getDisctanc(self,palyer):
        p1 = palyer.getCoordi()
        p2 = self.getCoordi()
        return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5

    # 获取第i个队友的色块范围
    def __get_party_slots(self):
        slot_start = 100
        start = slot_start + (self.i - 1) * 6
        end = start + 6
        return {"start": start, "end": end}
