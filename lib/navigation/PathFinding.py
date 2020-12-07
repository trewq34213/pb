# -*- coding:utf8 -*-
import time
import math
import random
from lib.control.Control import Control
from lib.unit.Player import Player
from lib.unit.Target import Target
from lib.struct.Point import Point
from lib.navigation.NvBase import NvBase
import os


# 地图坐标系自动寻路径
class Pathfinding(NvBase):
    w_down = 0 #w键是否按下标识

    def __init__(self, control: Control, player: Player):
        NvBase.__init__(self)
        self.control = control
        self.player = player
        self.hander = open("tmp/logs/" + self.getFormatTime(False) + "_pathfinding.log", 'a+')

    # 人物当前坐标
    def getNowPos(self):
        return self.player.getCoordi()

    # 找到最近的点后，削减路点数组，让最近的点成为第一点
    def reduceAllPoints(self, all_pos):
        near_pos = self.getNearstPoint(self.getNowPos(), all_pos)
        print("near_pos:" + near_pos.toString())
        for i in range(len(all_pos)):
            if all_pos[i].x == near_pos.x and all_pos[i].y == near_pos.y:
                return all_pos[i:]

    # 尝试摆脱卡住
    def unStuck(self):
        from lib.tools.mail import sendmail
        from run.config.UserConfig import UserConfig
        from lib.navigation.EnemyFinder import EnemyFinder
        sendmail(UserConfig.email, self.player.getName() + " more than 60s to next point", "", img=self.screenshot("stuck"))
        finder = EnemyFinder(player=self.player,control=self.control)
        if self.w_down == 1:
            finder.turn_back()
        finder.clear_target()
        self.control.driver.tap_key_down("w")
        self.w_down = 1
        count = 0
        while count < 10 and self.player.getStatus()['combat'] == 0:
            finder.random_behavior()
            count = count + 1
        self.control.driver.tap_key_up("w")
        self.w_down = 0

    # 自动寻路
    # 思路：以起始坐标开始，让人物持续移动，每隔一段时间读取当前坐标与上一次坐标和目的坐标3点绘制3角形
    #      通过直线方程确定应该左转还是右转，通过三角形夹角度数确定转向的幅度
    #      如此方式不断修正方向，直到夹角小于1度朝着目标点移动。
    # targetPos:本该的下一个目标点
    # all_targets:所有目标点
    # move_type:移动方式，0为边移动变修正方向，1为停止移动修正方向后再继续
    # sleep:修正间隔时间
    # precision: 误差距离  0.3误差大概10码左右
    # last :持续时间，到达持续时间如果还没有到达也终止，0表示一直持续
    # combat_exit : 进入战斗后是否退出寻路
    # alive_exit : 复活后是否退出寻路
    def walk(self, targetPos: Point, move_type=0, sleep=0.5, precision=0.3, last=0, combat_exit=False,alive_exit=False,checkMount=False,targetIsEnemy_exit=False):
        print("\r\n", file=self.hander)

        # 初始化起始位置和当前位置相同
        startPos = self.getNowPos()
        nowPos = startPos
        tx = targetPos.x
        ty = targetPos.y

        # 解决路点第一个点和人物重合，人物会再返回第一个点的问题
        d = self.get_distance_off_tow_pos(targetPos, nowPos)
        if d <= precision:
            print("起始点就是目标点，循环次数：0,X误差：" + str(abs(tx - nowPos.x)) + ",Y误差：" + str(abs(ty - nowPos.y)), file=self.hander)
            return True

        self.control.driver.tap_key_down("w")  # 开始持续移动
        self.w_down = 1  # w是否按下标志位
        count = 0
        start = time.time()

        while True:
            if time.time() - start > 60: # 超过一段时间还没有到达下一额点
                self.unStuck()
                start = time.time()

            if targetIsEnemy_exit and Target().isEnemy(self.player.getLevel()):
                if self.w_down == 1:
                    self.control.driver.tap_key_up("w")
                return False
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
            print(startPos.toString(), nowPos.toString(), targetPos.toString(), file=self.hander)

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

                    if move_type == 1 or t >= sleep: # 如果move_type == 1 或者转向角度较大,停下来转，否则行走中转
                        self.control.driver.tap_key_up("w")  # 转向期间停止移动
                        self.w_down = 0

                    if turn == 'left':
                        self.control.driver.turn_left(t)
                    else:
                        self.control.driver.turn_right(t)
                    count = count + 1
            else:
                self.control.driver.tap_key_up("w")  # 停止移动
                print("到达目标点，循环次数：" + str(count) + ",X误差：" + str(abs(tx - nowPos.x)) + ",Y误差：" + str(abs(ty - nowPos.y)), file=self.hander)
                return True
