# -*- coding:utf8 -*-

from lib.navigation.WorldPathFinding import WorldPathFinding
from lib.control.Control import Control
from lib.unit.Player import Player
from lib.tools.mail import sendmail
from run.config.UserConfig import UserConfig
from lib.struct.CoordiPoint import CoordiPoint
from lib.struct.WorldPoint import WorldPoint
from lib.config.SysConfig import SysConfig
from lib.base.Base import Base
from lib.bag.Bag import Bag
import os
import datetime
import time
import random


# 自定义来回寻路
class ChoicePathFinding(Base):
    def __init__(self, control: Control, player: Player, move_type=0, checkMount=True, type='p'):
        Base.__init__(self)
        self.player = player
        self.control = control
        self.move_type = move_type
        self.playerName = self.player.getName()
        self.checkMount = checkMount
        self.type = type
        self.hander_reapir = open("tmp/logs/" + self.getFormatTime(False) + "_choice_pathfinding.log", 'a+')

    # 从区域到营地
    def to_repair_run(self):
        if os.path.exists(SysConfig.record_path + "DynamicConfig.py"):
            from run.record.path_data.DynamicConfig import DynamicConfig
            if DynamicConfig.repair_path == 0 or DynamicConfig.repair_path == []:
                return False
        else:
            print("没有动态配置文件")
            os._exit(0)
        print("to cap #################################################################qr")
        all_pos = []
        reverse = DynamicConfig.repair_path[::-1]  # 因为录制的时候是从修理点到区域的，现在回去修理所以需要反转
        for i in reverse:
            if self.type == 'p':
                point = CoordiPoint(float(i[0]), float(i[1]))
            else:
                point = WorldPoint(float(i[2]), float(i[3]))
            all_pos.append(point)
        run_ret = self.inner_run(all_pos)
        if not run_ret:
            return False
        print("路点已完成")
        print("路点已完成: " + str(datetime.datetime.now()), file=self.hander_reapir)
        #self.control.driver.tap_str(" ")
        #sendmail(UserConfig.email, self.playerName + " arrive repair point", "", img=self.screenshot("arraive_repair_point"))
        return True

    # 从修理点到区域寻路
    def to_area_run(self):
        if os.path.exists(SysConfig.record_path + "DynamicConfig.py"):
            from run.record.path_data.DynamicConfig import DynamicConfig
        else:
            print("没有动态配置文件")
            os._exit(0)

        all_pos = []
        for i in DynamicConfig.repair_path:
            if self.type == 'p':
                point = CoordiPoint(float(i[0]), float(i[1]))
            else:
                point = WorldPoint(float(i[2]), float(i[3]))
            all_pos.append(point)
        run_ret = self.inner_run(all_pos)
        if not run_ret:
            return False
        print("路点已完成，已到区域")
        print("路点已完成，已到区域: " + str(datetime.datetime.now()), file=self.hander_reapir)
        #self.control.driver.tap_str(" ")
        #sendmail(UserConfig.email, self.playerName + " arrive area point", "", img=self.screenshot("arraive_area_point"))
        return True

    # 寻路（寻路中进入战斗不停下来）
    def inner_run(self, all_pos):
        if self.type == 'p':
            from lib.navigation.PathFinding import Pathfinding
            finder = Pathfinding(control=self.control, player=self.player)
            precision = 0.25
        else:
            finder = WorldPathFinding(control=self.control, player=self.player)
            precision = 5
        all_pos = finder.reduceAllPoints(all_pos)
        for w in all_pos:
            status = self.player.getStatus()
            if status["dead"] == 1 or status["is_ghost"] == 1:
                print("路上挂了，尝试跑尸吧")
                print("路上挂了，尝试跑尸吧:" + str(datetime.datetime.now()), file=self.hander_reapir)
                sendmail(UserConfig.email, self.playerName + " repair dead", "", img=self.screenshot("repair_dead"))
                return False

            self.player.not_combat_recover()
            self.player.combat_recover()
            print("repair run target pos:")
            print(w.toString())
            ret = finder.walk(w, move_type=self.move_type, combat_exit=False, checkMount=self.checkMount,sleep=0.25,precision=precision)
            # all_pos = finder.reduceAllPoints(all_pos)
            if not ret:
                return False
        return True

    # 去到一个点
    def walk_to_last_point(self, tp=None):
        if self.player.getStatus()["dead"] == 1:
            return
        if os.path.exists(SysConfig.record_path + "DynamicConfig.py"):
            from run.record.path_data.DynamicConfig import DynamicConfig
        else:
            print("没有动态配置文件")
            os._exit(0)

        last_point = DynamicConfig.repair_path[::-1][0]  # repair_path的最后一个点

        if self.type == 'p':
            from lib.navigation.PathFinding import Pathfinding
            finder = Pathfinding(control=self.control, player=self.player)
            precision = 0.3
            p = tp if tp is not None else CoordiPoint(last_point[0], last_point[1])
        else:
            finder = WorldPathFinding(control=self.control, player=self.player)
            precision = 5
            p = tp if tp is not None else WorldPoint(last_point[2], last_point[3])

        if finder.get_distance_off_tow_pos(finder.getNowPos(), p) > precision:
            finder.walk(p, move_type=self.move_type, combat_exit=False, checkMount=self.checkMount)
