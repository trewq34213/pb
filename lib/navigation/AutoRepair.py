# -*- coding:utf8 -*-

from lib.navigation.WorldPathFinding import WorldPathFinding
from lib.control.Control import Control
from lib.unit.Player import Player
from lib.tools.mail import sendmail
from run.config.UserConfig import UserConfig
from lib.struct.CoordiPoint import CoordiPoint
from lib.struct.WorldPoint import WorldPoint
from lib.config.SysConfig import SysConfig
from lib.bag.Bag import Bag
import os
import datetime
import time
import random


# 自动修理
class AutoRepair(WorldPathFinding):
    def __init__(self, control: Control, player: Player, move_type=0,checkMount=True):
        WorldPathFinding.__init__(self, control=control, player=player)
        self.move_type = move_type
        self.hander_reapir = open("tmp/logs/" + self.getFormatTime(False) + "_auto_repair.log", 'a+')
        self.playerName = self.player.getName()
        self.checkMount = checkMount

    # 自动修理入口
    def repair(self):
        if not self.to_repair_run():
            return False
        if not self.do_repair():
            return False
        if not self.to_area_run():
            return False

    # 从区域到自动修理寻路
    def to_repair_run(self):
        if os.path.exists(SysConfig.record_path + "DynamicConfig.py"):
            from run.record.path_data.DynamicConfig import DynamicConfig
            if DynamicConfig.repair_path == 0 or DynamicConfig.repair_path == []: # 没有修理路点
                return False
        else:
            print("没有动态配置文件")
            os._exit(0)
        print("to repair #################################################################qr")
        all_world_pos = []
        reverse = DynamicConfig.repair_path[::-1]  # 因为录制的时候是从修理点到区域的，现在回去修理所以需要反转
        for i in reverse:
            world = WorldPoint(float(i[2]), float(i[3]))
            all_world_pos.append(world)
        run_ret = self.inner_run(all_world_pos)
        if not run_ret:
            return False
        print("路点已完成，即将开始修理")
        print("路点已完成，即将开始修理: " + str(datetime.datetime.now()), file=self.hander_reapir)
        self.control.driver.tap_str(" ")
        sendmail(UserConfig.email, self.playerName + " arrive repair point", "", img=self.screenshot("arraive_repair_point"))
        return True

    # 从修理点到区域寻路
    def to_area_run(self):
        if os.path.exists(SysConfig.record_path + "DynamicConfig.py"):
            from run.record.path_data.DynamicConfig import DynamicConfig
        else:
            print("没有动态配置文件")
            os._exit(0)

        all_world_pos = []
        for i in DynamicConfig.repair_path:
            world = WorldPoint(float(i[2]), float(i[3]))
            all_world_pos.append(world)
        run_ret = self.inner_run(all_world_pos)
        if not run_ret:
            return False
        print("路点已完成，即将开始打怪")
        print("路点已完成，即将开始打怪: " + str(datetime.datetime.now()), file=self.hander_reapir)
        self.control.driver.tap_str(" ")
        sendmail(UserConfig.email, self.playerName + " arrive area point", "", img=self.screenshot("arraive_area_point"))
        return True

    # 寻路（寻路中进入战斗不停下来）
    def inner_run(self, all_world_pos):
        all_world_pos = self.reduceAllPoints(all_world_pos)
        for w in all_world_pos:
            status = self.player.getStatus()
            if status["dead"] == 1 or status["is_ghost"] == 1:
                print("修理路上挂了，尝试跑尸吧")
                print("修理路上挂了，尝试跑尸吧:" + str(datetime.datetime.now()), file=self.hander_reapir)
                sendmail(UserConfig.email, self.playerName + " repair dead", "", img=self.screenshot("repair_dead"))
                return False

            self.player.not_combat_recover()
            self.player.combat_recover()
            print("repair run target pos:")
            print(w.toString())
            ret = self.walk(w, move_type=self.move_type, combat_exit=False,checkMount=self.checkMount,sleep=0.3)
            if not ret:
                return False
        return True

    # 执行自动修理
    def do_repair(self):
        if os.path.exists(SysConfig.record_path + "DynamicConfig.py"):
            from run.record.path_data.DynamicConfig import DynamicConfig
        else:
            print("没有动态配置文件")
            os._exit(0)
        from lib.marco.Marco import Marco
        npc = DynamicConfig.repair_npc_name
        gossip_option = DynamicConfig.repair_npc_gossip
        marco = Marco(self.control)

        #执行修理前回调
        self.player.before_repair()
        time.sleep(2)

        #不管是否需要修理，先尝试修改里一波
        marco.selectTarget(npc)
        print("执行选中目标：" + npc)
        self.control.driver.tap_key("'")
        print("执行与目标交互：" + npc)
        time.sleep(5)
        if gossip_option > 0:
            marco.selectGossipOption(gossip_option)
        time.sleep(10)

        i = 0
        while i < 10 and (self.player.getStatus()["need_repair"] == 1 or Bag.isAllBagFull()):
            marco.selectTarget(npc)
            print("执行选中目标：" + npc)
            print("执行选中目标：" + npc + " " + str(datetime.datetime.now()), file=self.hander_reapir)
            self.control.driver.tap_key("'")
            print("执行与目标交互：" + npc)
            print("执行与目标交互：" + npc + " " + str(datetime.datetime.now()), file=self.hander_reapir)
            j = 0
            while j < 5 and (self.player.getStatus()["need_repair"] == 1 or Bag.isAllBagFull()):  # 防卡
                time.sleep(5)
                if gossip_option > 0:
                    marco.selectGossipOption(gossip_option)
                    time.sleep(10)
                self.control.driver.tap_str(" ")
                self.control.driver.tap_key("a") if random.randint(0, 1) == 0 else self.control.driver.tap_key("d")
                self.control.driver.tap_key("'")
                j = j + 1
            i = i + 1
        print("修理完成，即将返回区域：")
        print("修理完成，即将返回区域：" + str(datetime.datetime.now()), file=self.hander_reapir)
        sendmail(UserConfig.email, self.playerName + " repair done", "", img=self.screenshot("repair_done"))
        return True
