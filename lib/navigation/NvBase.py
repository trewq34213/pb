# -*- coding:utf8 -*-
import time
import math
import random
from lib.control.Control import Control
from lib.unit.Player import Player
from lib.struct.Point import Point
from lib.base.Base import Base


# 导航基类
class NvBase(Base):
    def __init__(self):
        Base.__init__(self)
        self.hander = open("tmp/logs/" + self.getFormatTime(False) + "_navbase.log", 'a+')

    # 获取坐标区域中里自己最近的点
    def getNearstPoint(self, now_pos: Point, all_pos):
        start = time.time()
        start_distance = float("inf")
        print("start_distance:" + str(start_distance))
        for pos in all_pos:
            now_distance = self.get_distance_off_tow_pos(pos, now_pos)
            print(pos.toString() + " now_distance:" + str(now_distance))
            if now_distance < start_distance:
                near_pos = pos
                start_distance = now_distance
        print("get_nearest_pos time:" + str(time.time() - start))
        return near_pos  # 别担心，这里肯定能找到，难道还有比无穷大更大的么！！！

    # 根据三点坐标计算角度（转向角度）
    # a为起始点和当前点那条边
    # b为起始点到目标点那条边
    # c为当前点到目标点那条边
    # 设：S为起始点，N为当前点，T为目标点
    # 先用勾股定理计算出三角形三边长，再用反余弦计算弧度和角度
    # 角度为ab的夹角度数 + bc夹角度数
    def posToDegree(self, startPos: Point, nowPos: Point, targetPos: Point):
        a = self.get_distance_off_tow_pos(startPos, nowPos)
        b = self.get_distance_off_tow_pos(startPos, targetPos)
        c = self.get_distance_off_tow_pos(nowPos, targetPos)
        print("a = " + str(a) + ", b = " + str(b) + ", c = " + str(c), file=self.hander)

        if a == 0:  # 为0可能卡地形了
            return 9999
        if b == 0:
            print("起始点和目标点重合了")
            print("起始点和目标点重合了", file=self.hander)
            return 0
        if c == 0:
            print("当前点点和目标点重合了")
            print("当前点点和目标点重合了", file=self.hander)
            return 0

        # 反余弦的参数值之必需在【-1,1】这个区间，由于电脑浮点数计算误差可能出现大于1或者小于-1的情况，这里要兼容处理下
        tmp = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)
        tmp = 1 if tmp >= 1 else tmp
        tmp = -1 if tmp <= -1 else tmp
        degreeNST = math.degrees(math.acos(tmp))  # 角NST的度数

        tmp = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
        tmp = 1 if tmp >= 1 else tmp
        tmp = -1 if tmp <= -1 else tmp
        degreeNTS = math.degrees(math.acos(tmp))  # 角NTS的度数

        degree = degreeNST + degreeNTS  # 实际要修正的角度应该是角SNT的补角，即三角形另外两个内角的和
        print("角度 = " + str(degree), file=self.hander)
        return degree

    # 计算两个点之间的距离（使用距离公式）
    def get_distance_off_tow_pos(self, p1: Point, p2: Point):
        return round(((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5, 8)

    # 判断应该左转还是右转，使用了直线方程
    def leftOrRight(self, startPos: Point, nowPos: Point, targetPos: Point):
        x1 = startPos.x
        y1 = startPos.y
        x2 = targetPos.x
        y2 = targetPos.y
        X = nowPos.x
        Y = nowPos.y

        # 特殊情况（基本不可能出现）：起始坐标和目的坐标的x轴数据相同，则是垂直于x轴的直线，无斜率
        if x1 == x2:
            if X < x1:  # 目的坐标在直线左边
                if Y < y2:  # 目的坐标在当前坐标上面
                    return 'right'
                return 'left'
            else:  # 目的坐标在直线右边
                if Y < y2:  # 目的坐标在当前左边下面
                    return 'left'
                return 'right'

        # 构建起始点到目标点两点直线方程为：y = kx + b, 那么给定一点当前点P(X,Y)如果kX+b>Y,则P在直线下方,反之则在上方,相等表明在直线上.
        k = (y2 - y1) / (x2 - x1)  # 斜率
        b = y1 - k * x1  # 截距
        print("直线方程：y = " + str(k) + "x + " + str(b), file=self.hander)
        ret = k * X + b  # 将当前坐标带入直线方程看看该坐标在直线上方还是在直线下方

        if ret >= Y:  # 在下方
            print("当前点在直线下方", file=self.hander)
            if x2 < X:
                return 'left'
            return 'right'
        else:  # 在上方
            print("当前点在直线上方", file=self.hander)
            if x2 > X:
                return 'left'
            return 'right'

    # @Deprecated
    # 向量叉积法计算当前点在目标点与起始点所在直线的左侧还是右侧
    # 设起始点为S 当前点为N 目标点为T
    def leftOrRightByVector(self, startPos: Point, nowPos: Point, targetPos: Point):
        X = nowPos.x
        Y = nowPos.y
        ST = Point(targetPos.x - startPos.x, targetPos.y - startPos.y)  # 起始点到目标点向量
        SN = Point(nowPos.x - startPos.x, nowPos.y - startPos.y)  # 起始点到当前点向量
        ds = (ST.x * SN.y) - (SN.x * ST.y)  # 向量叉积
        if ds > 0:  # 在直线左边
            if Y < targetPos.y:
                return "left"
            return "right"
        elif ds < 0:  # 在直线右边
            if Y < targetPos.y:
                return "right"
            return "left"
        else:  # 在直线上
            return "on the line"

    # 根据朝向计算左右转（使用facing）
    def leftOrRightByFacing(self, playerFacing, nowPos: Point, targetPos: Point):
        slope = self.calNowToTargetFacing(nowPos, targetPos)
        directionDiff = slope - playerFacing  # 目标点弧度与当前弧度差
        print("弧度差：" + str(directionDiff), file=self.hander)
        if directionDiff > math.pi:
            directionDiff = ((math.pi * 2) - directionDiff) * -1  # 大于180° 取另一个角，即360°-directionDiff，并且取负
        if directionDiff < -math.pi:
            directionDiff = (math.pi * 2) - (directionDiff * -1)  # 小于负180° 其实和大于180°一个意思，同样取晓得一个角，并且取正

        print("处理后的弧度差：" + str(directionDiff), file=self.hander)
        if directionDiff > 0:
            return "left"
        return "right"

    # 计算当前点到目标点的弧度
    def calNowToTargetFacing(self, nowPos: Point, targetPos: Point):
        slope = math.atan2(targetPos.y - nowPos.y, nowPos.x - targetPos.x)  # 反正切计算方位角弧度，即与x轴夹角
        print("反正切值：" + str(slope), file=self.hander)
        slope = slope + math.pi  # 因为反正切函数值域为(-π/2,π/2),需要给他转换到0-2π范围
        slope = slope - math.pi * 0.5  # 此弧度是从当前点到目标点的绝对弧度，需要转换成wow的弧度，左旋90°。使上（北）为0,而不是右，和wow保持一致
        if slope < 0:
            slope = slope + math.pi * 2  # 确保弧度不是一个负数

        if slope > math.pi * 2:  # 也要确保弧度不会超过2π
            slope = slope - math.pi * 2
        print("反正切值处理后的值：" + str(slope), file=self.hander)
        return slope

    # 根据角度计算转向时间（幅度），测试0.52秒大概90度
    def degreeToTime(self, degree):
        one_degree_time = 0.51 / 90  # 转1度需要多少秒
        return one_degree_time * degree

    # 坐标系顺时针旋转degree
    def clockWiseSpin(self, point: Point, degree):
        x = point.x * math.cos(math.radians(degree)) + point.y * math.sin(math.radians(degree))
        y = point.y * math.cos(math.radians(degree)) - point.x * math.sin(math.radians(degree))
        return Point(x, y)

    # 坐标系逆时针旋转degree
    def counterClockWiseSpin(self, point: Point, degree):
        x = point.x * math.cos(math.radians(degree)) - point.y * math.sin(math.radians(degree))
        y = point.y * math.cos(math.radians(degree)) + point.x * math.sin(math.radians(degree))
        return Point(x, y)
