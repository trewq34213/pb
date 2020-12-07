# -*- coding:utf8 -*-
import time
import math
import random
import os
from lib.control.Control import Control
from lib.unit.Player import Player
from lib.struct.CoordiPoint import CoordiPoint
from lib.struct.WorldPoint import WorldPoint
from lib.struct.Point import Point
from lib.navigation.PathFinding import Pathfinding


# 路点寻怪策略实现
class StrageyFinderpath(Pathfinding):
    now_pos = None

    def __init__(self, control: Control, player: Player):
        Pathfinding.__init__(self, control=control, player=player)
        from run.record.path_data.DynamicConfig import DynamicConfig
        self.finder_path = DynamicConfig.finder_path
        self.hander = open("tmp/logs/" + self.getFormatTime(False) + "_strageyFinderpath.log", 'a+')

    # 获取离玩家最近的一个点
    def get_nearst_pos(self):
        start_distance = float("inf")
        for tmp in self.finder_path:
            pos = CoordiPoint(x=tmp[0], y=tmp[1])
            now_distance = self.get_distance_off_tow_pos(pos, self.player.getCoordi())
            if now_distance < start_distance:
                near_pos = pos
                start_distance = now_distance
        self.now_pos = near_pos
        return near_pos  # 别担心，这里肯定能找到，难道还有比无穷大更大的么！！！

    # 获取当前路点的下一个路点
    def get_next_pos(self):
        if self.now_pos is None:
            raise Exception("当前路点未确定，请先使用get_nearst_pos获取当前路点")

        for index in range(len(self.finder_path)):
            if self.now_pos.x == self.finder_path[index][0] and self.now_pos.y == self.finder_path[index][1]:
                if index + 1 >= len(self.finder_path):
                    return CoordiPoint(self.finder_path[0][0], self.finder_path[0][1])
                return CoordiPoint(self.finder_path[index + 1][0], self.finder_path[index + 1][1])
