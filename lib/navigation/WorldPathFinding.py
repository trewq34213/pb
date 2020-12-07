# -*- coding:utf8 -*-
import time
import math
import random
from lib.control.Control import Control
from lib.unit.Player import Player
from lib.struct.CoordiPoint import CoordiPoint
from lib.struct.WorldPoint import WorldPoint
from lib.struct.Point import Point
from lib.navigation.PathFinding import Pathfinding


# 世界坐标的1表示1码，而人物的移动速度是7.111码/s

# 使用世界坐标的寻路
class WorldPathFinding(Pathfinding):
    def __init__(self, control: Control, player: Player):
        Pathfinding.__init__(self, control=control, player=player)
        self.hander = open("tmp/logs/" + self.getFormatTime(False) + "_worldpathfinding.log", 'a+')

    # 获取人物当前世界坐标
    def getNowPos(self):
        try:
            area = self.player.getArea()
            return self.player.getCoordi().to_world(area=area)
        except Exception as e:
            return self.getNowPos()

    def walk(self, targetPos: WorldPoint, move_type=0, sleep=0.5, precision=5, last=0, combat_exit=False, alive_exit=False, checkMount=False):
        print("\r\n", file=self.hander)

        # 初始化起始位置和当前位置相同
        startPos = self.getNowPos()
        nowPos = startPos
        tx = targetPos.x
        ty = targetPos.y

        # 解决路点第一个点和人物重合，人物会再返回第一个点的问题
        # d = self.get_distance_off_tow_pos(targetPos, nowPos)
        # if d <= precision:
        #     print("起始点就是目标点，循环次数：0,X误差：" + str(abs(tx - nowPos.x)) + ",Y误差：" + str(abs(ty - nowPos.y)), file=self.hander)
        #     return True

        self.control.driver.tap_key_down("w")  # 开始持续移动
        self.w_down = 1  # w是否按下标志位
        count = 0
        start = time.time()

        while True:
            if time.time() - start > 60: # 超过一段时间还没有到达下一额点
                self.unStuck()
                start = time.time()
            if combat_exit is True and self.player.getStatus()["combat"] == 1:
                if self.w_down == 1:
                    self.control.driver.tap_key_up("w")
                return False
            if checkMount and self.player.getStatus()['mounted'] == 0 and self.player.getStatus()['combat'] == 0:
                if self.w_down == 1:
                    self.control.driver.tap_key_up("w")
                self.player.mounted()
                self.control.driver.tap_key_down("w")  # 开始持续移动
                self.w_down = 1  # w是否按下标志位
            if alive_exit is True and self.player.getStatus()['dead'] == 0:
                if self.w_down == 1:
                    self.control.driver.tap_key_up("w")
                return False
            print("开始" + str(count), file=self.hander)
            if time.time() - start > last > 0:
                if self.w_down == 1:
                    self.control.driver.tap_key_up("w")
                return False

            if self.w_down == 0:
                self.control.driver.tap_key_down("w")
                self.w_down = 1
            startPos = nowPos  # 变更起始位置为上次当前位置
            time.sleep(sleep)
            nowPos = self.getNowPos()
            print("start:" + startPos.toString(), file=self.hander)
            print("now:" + nowPos.toString(), file=self.hander)
            print("target:" + targetPos.toString(), file=self.hander)

            distance_to_target = self.get_distance_off_tow_pos(nowPos, targetPos)
            print("与目标距离：" + str(distance_to_target), file=self.hander)
            if distance_to_target > precision:
                degree = self.posToDegree(startPos, nowPos, targetPos)
                while degree == 9999:
                    if self.w_down == 0:
                        self.control.driver.tap_key_down("w")  # 开始持续移动
                        self.w_down = 1
                    self.control.driver.turn_right()
                    self.control.driver.tap_str(" ")  # 跳
                    print("寻路跳")
                    print("跳", file=self.hander)
                    degree = self.posToDegree(startPos, self.getNowPos(), targetPos)

                t = self.degreeToTime(degree)
                print("转向时间 t = " + str(t), file=self.hander)
                if t > 0:
                    turn = self.leftOrRight(startPos, nowPos, targetPos)
                    print("turn = " + turn, file=self.hander)

                    if move_type == 1 or t >= sleep:
                        self.control.driver.tap_key_up("w")  # 转向期间停止移动
                        self.w_down = 0

                    # todo 为何使用世界坐标系，左右转要颠倒呢
                    if turn == 'right':
                        self.control.driver.turn_left(t)
                    else:
                        self.control.driver.turn_right(t)
                    count = count + 1
            else:
                self.control.driver.tap_key_up("w")  # 停止移动
                print("到达目标点，循环次数：" + str(count) + ",X误差：" + str(abs(tx - nowPos.x)) + ",Y误差：" + str(abs(ty - nowPos.y)), file=self.hander)
                return True
