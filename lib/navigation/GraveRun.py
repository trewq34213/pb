# -*- coding:utf8 -*-

from lib.navigation.PathFinding import Pathfinding
from lib.control.Control import Control
from lib.unit.Player import Player
from lib.recorder.PathRecorder import PathRecorder
from lib.tools.mail import sendmail
from run.config.UserConfig import UserConfig
from lib.struct.CoordiPoint import CoordiPoint
from lib.config.SysConfig import SysConfig
import os

# 自动跑尸
class GraveRun(Pathfinding):

    def __init__(self, control: Control, player: Player, move_type=0):
        Pathfinding.__init__(self, control=control, player=player)
        self.move_type = move_type
        self.hander_grave = open("tmp/logs/" + self.getFormatTime(False) + "_graverun.log", 'a+')

    # 跑尸
    def grave_run(self):
        corpseCoordi = self.player.getCropsCoordi()
        if corpseCoordi.x == 0 or corpseCoordi.y == 0:
            sendmail(UserConfig.email, self.player.getName() + "can't get corpse pos", "", img=self.screenshot("cant_get_corpse_pos"))
            os._exit(0)

        grave_path = []
        if os.path.exists(SysConfig.record_path + "DynamicConfig.py"):
            from run.record.path_data.DynamicConfig import DynamicConfig
            grave_path = DynamicConfig.grave_path

        all_points = []
        if grave_path == 0 or grave_path == []:
            print("没有路点配置，直接跑向尸体")
            print("没有路点配置，直接跑向尸体", file=self.hander_grave)
            all_points = [corpseCoordi]
        else:
            for i in grave_path:
                #pos = i.split(",")  # 将坐标转换成数组
                all_points.append(CoordiPoint(float(i[0]), float(i[1])))
            all_points = self.reduceAllPoints(all_points)

        for coordi in all_points:
            if self.player.getStatus()["dead"] == 0:
                break
            print("grave run target pos:")
            print("grave run target pos:", file=self.hander_grave)
            print(coordi.toString())

            # 先跑到区域中点
            self.walk(
                coordi,
                move_type=self.move_type,
                alive_exit=True, # 一旦复活就停止寻路
                combat_exit=True, # 这里需要进入战斗退出，因为复活的时候可能路点还没有走完
                checkMount=False
            )

        if self.player.getStatus()["dead"] == 0:
            print("路点没有走完就复活，666")
            print("路点没有走完就复活，666", file=self.hander_grave)
            sendmail(UserConfig.email, self.player.getName() + "resurrected not walk all points", "", img=self.screenshot("resurrected"))
            return True

        print("路点已完成，即将走向尸体坐标")
        print("路点已完成，即将走向尸体坐标", file=self.hander_grave)
        self.control.driver.tap_str(" ")
        print(self.player.getCoordi().toString(), corpseCoordi.toString())
        while self.player.getStatus()["dead"] == 1:
            self.walk(corpseCoordi, self.move_type,combat_exit=True,alive_exit=True) # 只要是复活了或者进入战斗了，就退出寻路
        sendmail(UserConfig.email, self.player.getName() + "resurrected", "", img=self.screenshot("resurrected"))
