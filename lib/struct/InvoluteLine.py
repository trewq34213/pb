# -*- coding:utf8 -*-
from lib.struct.CoordiPoint import CoordiPoint
from lib.base.Base import Base
from lib.navigation.AreaFighting import AreaFighting
from lib.navigation.NvBase import NvBase
import math


# 渐开线，实现了圆形和方形
class InvoluteLine(Base):
    def __init__(self, area_pos):
        super().__init__()
        self.area_pos = area_pos  # 区域

    # 获取区域中心点
    def get_center_point(self):
        left_top = self.area_pos["leftTop"]
        right_bottom = self.area_pos["rightBottom"]
        center = [(left_top[0] + right_bottom[0]) / 2, (left_top[1] + right_bottom[1]) / 2]
        return CoordiPoint(center[0], center[1])

    # 获取圆形渐开线上所有的点
    def get_circle_all_points(self, d, r):
        center = self.get_center_point()
        n = 0
        ret = []
        done = False
        while not done:
            while n < 2 * math.pi:
                x = center.x + r * math.cos(n)
                y = center.y - r * math.sin(n)
                p = CoordiPoint(x, y)
                if not AreaFighting.pos_in_area(p, self.area_pos):
                    return ret
                ret.append(p)
                n = n + d / r
            n = 0
            r = r + r
        return ret

    # 获取圆形渐开线离玩家最近一个点
    def get_circle_near_point(self, nowPos:CoordiPoint, d, r):
        center = self.get_center_point()
        if not AreaFighting.pos_in_area(nowPos, self.area_pos):
            return center
        all = self.get_circle_all_points(d, r)
        near = NvBase().getNearstPoint(nowPos, all)
        return CoordiPoint(near.x, near.y)

    # 获取圆形渐开线上的下一个点
    def get_circle_next_point(self,nowPos,d,r):
        near = self.get_circle_near_point(nowPos,d,r)
        center = self.get_center_point()
        all = self.get_circle_all_points(d,r)
        length = len(all)
        for i in range(length):
            if near.x == all[i].x and near.y == all[i].y:
                if i+1 < length:
                    return all[i+1]
        return center

        # 获取方形渐开线上所有的点
    def get_square_all_points(self, v):
        center = self.get_center_point()
        x = center.x
        y = center.y
        tmp = 1
        ret = []
        done = False
        while not done:
            j = 0
            k = v
            for t in range(2):
                for i in range(tmp):
                    x = x + j
                    y = y + k
                    p = CoordiPoint(x, y)
                    if not AreaFighting.pos_in_area(p, self.area_pos):
                        return ret
                    ret.append(p)
                j = v
                k = 0
            tmp = tmp + 1
            v = v * -1
        return ret

    # 获取方形渐开线上离玩家最近的一个点
    def get_square_near_point(self, nowPos:CoordiPoint, v):
        center = self.get_center_point()
        if not AreaFighting.pos_in_area(nowPos, self.area_pos):
            return CoordiPoint(center.x, center.y)
        all = self.get_square_all_points(v)
        near = NvBase().getNearstPoint(nowPos, all)
        return CoordiPoint(near.x, near.y)

    # 获取方形渐开线上的下一个点
    def get_square_next_point(self,nowPos,v):
        near = self.get_square_near_point(nowPos,v)
        center = self.get_center_point()
        all = self.get_square_all_points(v)
        length = len(all)
        for i in range(length):
            if near.x == all[i].x and near.y == all[i].y:
                if i+1 < length:
                    return all[i+1]
        return center
