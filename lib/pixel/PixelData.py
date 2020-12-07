# -*- coding:utf8 -*-
from lib.base.Base import Base
import win32api, win32con
from run.config.UserConfig import UserConfig
from lib.struct.PixelPonit import PixelPoint
import math

# 像素工具类
class PixelData(Base):

    # 获取第index块像素区域的坐标
    @staticmethod
    def getPointByIndex(index):
        distance = PixelData.getPixelDistance()
        x = int(UserConfig.start_pos.x + distance * index)
        y = UserConfig.start_pos.y
        return PixelPoint(x, y)

    # 获取屏幕分辨率
    @staticmethod
    def getScreenResolution():
        x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        return PixelPoint(x, y)

    # 获取数据像素块之间的距离
    @staticmethod
    def getPixelDistance():
        return UserConfig.distance

    # 获取一段像素字符串
    @staticmethod
    def get_points_string(startIndex, endIndex):
        c = ""
        i = startIndex
        while i < endIndex:
            point = PixelData.getPointByIndex(i)
            tmp = point.getString()
            if tmp == "":
                return c
            c = c + point.getString()
            i = i + 1
        return c

    # 获取像素位的bool值
    @staticmethod
    def get_point_bools(index, max):
        point = PixelData.getPointByIndex(index)
        base2Operation = point.getInt()
        ret = []
        i = max
        while i >= 0:
            active = 1 if base2Operation - math.pow(2, i) >= 0 else 0
            ret.append(active)
            if active == 1:
                base2Operation = base2Operation - math.pow(2, i)
            i = i - 1
        return ret[::-1]

    # 获取像素位的bool值（使用位运算的方式）
    @staticmethod
    def get_point_bools_bit(index, max):
        point = PixelData.getPointByIndex(index)
        base2Operation = point.getInt()
        ret = []
        for i in range(max + 1):
            tmp = (base2Operation & (2 ** i)) >> i  # bool整数的第i位与2**i方按位与运算再右移i位，对应位为1结果为1否则为0
            ret.append(tmp)
        return ret

    # 坐标换算
    @staticmethod
    def get_another_resolution_point(point: PixelPoint):
        myRes = PixelPoint(1920, 1080)
        res = PixelData.getScreenResolution()
        newX = int(point.x / myRes.x * res.x)
        newY = int(point.y / myRes.y * res.y)
        return PixelPoint(newX, newY)
