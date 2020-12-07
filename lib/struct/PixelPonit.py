# -*- coding:utf8 -*-
from lib.struct.Point import Point
from lib.base.Base import Base
import random


# 表示屏幕的一个像素坐标
class PixelPoint(Point):
    def __init__(self, x, y):
        Point.__init__(self, x, y)

    # 获取像素整形值
    def getInt(self, mod=1):
        rgb = self.getRGB()
        return int(int(Base.RGB_to_Hex(rgb), 16) / mod)

    # 获取像素浮点值
    def getFloat(self, mod=1):
        rgb = self.getRGB()
        return int(Base.RGB_to_Hex(rgb), 16) / mod

    # 获取像素bool值
    def getBool(self, mod=1):
        int_num = self.getInt(mod)
        return True if int_num > 0 else False

    # 获取像素列符串值
    def getString(self, mod=1):
        rgb = self.getRGB()
        int_num = self.getInt(mod)
        if int_num < 1114112 and rgb[0] != 63 and rgb[1] != 63:  # unicode最大编码为：1114112，r=63，g=63表示没有使用的块
            c = chr(int(int_num))
        else:
            c = ""
        return c

    # 获取像素rgb数组
    def getRGB(self):
        return Base.get_color_RGB(self.x, self.y)

    # 混淆一个点的x，y，避免一直使用一个点造成bot感觉
    def confoundPoint(self, rang=10):
        randx = random.uniform(0, 1)
        self.x = int(self.x + random.uniform(0, rang)) if randx == 0 else int(self.x - random.uniform(0, rang))
        randy = random.uniform(0, 1)
        self.y = int(self.y + random.uniform(0, rang)) if randy == 0 else int(self.y - random.uniform(0, rang))
        return self
