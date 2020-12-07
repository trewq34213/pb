# -*- coding:utf8 -*-
import math
import multiprocessing
from lib.unit.Unit import Unit
from lib.pixel.PixelData import PixelData
from lib.config.SysConfig import SysConfig
from lib.base.Base import Base
from lib.unit.Player import Player
from lib.unit.Target import Target
from lib.control.Control import Control
from run.config.UserConfig import UserConfig
from lib.tools.mail import sendmail
from lib.spell.Spell import Spell
from lib.navigation.AreaFighting import AreaFighting
from lib.control.Pyinput import Pyinput

import time
import random
import os


# 在新进程里按tab找怪
def tab_thread(got):
    if hasattr(UserConfig,"use_name_finder") and UserConfig.use_name_finder:
        from lib.NameFinder.NpcNameFinder import NpcNameFinder
        finder = NpcNameFinder()
    while not Target().isEnemy(Player().getLevel()) and Player().getStatus()['dead'] == 0:
        Pyinput().tap_key("tab")
        time.sleep(random.uniform(0.1, 0.3))
        if hasattr(UserConfig, "use_name_finder") and UserConfig.use_name_finder:
            finder.findAndClick()
    got.value = 1
    print("find enemy， process tab end .............")


# 在新进程里使用NpcNameFinder找怪
# def namefinder_thread(got):
#     from lib.NameFinder.NpcNameFinder import NpcNameFinder
#     finder = NpcNameFinder()
#     while not Target().isEnemy(Player().getLevel()) and Player().getStatus()['dead'] == 0:
#         finder.findAndClick()
#     got.value = 1
#     print("find enemy， process namefinder end .............")


class EnemyFinder(Base):
    def __init__(self, player: Player, control: Control):
        Base.__init__(self)
        self.player = player
        self.control = control
        self.spell = Spell(control)
        self.move_count = 0

    # 找敌人，找到返回敌人
    def find_enemy(self):
        self.player.before_findenemy()
        print("begin find enemy")
        from run.record.path_data.DynamicConfig import DynamicConfig
        start = time_without_enemy = time.time()
        playerLevel = self.player.getLevel()

        got = multiprocessing.Value("d", 0)  # 多进程共享变量
        # 寻怪进程
        p = multiprocessing.Process(target=tab_thread, args=(got,))
        p.start()

        while True:
            if self.player.getStatus()['dead'] == 1:
                return Target()
            if Target().isEnemy(playerLevel):
                print("end find enemy 1")
                return Target()

            Player.someBodyWihsperMe(self.player.getName())
            playerStatus = self.player.getStatus()

            if playerStatus["dead"] == 1 or playerStatus["is_ghost"] == 1:
                print("end find enemy 2")
                return Target()
            if playerStatus["combat"] == 1:
                time.sleep(0.5)  # 等待自动选中敌人
                if Target().isEnemy(playerLevel):
                    print("end find enemy 3")
                    return Target()

            # 区域打怪判断
            if DynamicConfig.area_fighting_pos != 0:
                AreaFighting(control=self.control, player=self.player, area_pos=DynamicConfig.area_fighting_pos).goto_area()

            if time.time() - time_without_enemy > UserConfig.time_without_enemy:
                sendmail(UserConfig.email, self.player.getName() + " more than " + str(UserConfig.time_without_enemy), "", self.screenshot("time_without_enemy"))
                time_without_enemy = time.time()

            spend = time.time() - start
            if spend > 60:  # 如果1分钟都还没有找到敌人，那么很有可能卡地形了，则转身,重置循环条件
                print("超过60秒没有找到敌人，判定为卡地形，转身，重置查找时间")
                self.turn_back()
                start = time.time()

            # self.control.driver.tap_key("tab")  # 先用tab在寻怪
            target = Target()
            if target.isEnemy(playerLevel):
                print("end find enemy 4")
                return target

            if UserConfig.check_touch_by_other == 1 and target.isTouchByAnoter() is True:
                self.clear_target()

            # 寻怪策略
            if UserConfig.find_enemy_strategy == 1 and DynamicConfig.area_fighting_pos != 0:
                self.strategy_circle_involute(DynamicConfig.area_fighting_pos, got)
            elif UserConfig.find_enemy_strategy == 2 and DynamicConfig.area_fighting_pos != 0:
                self.strategy_square_involute(DynamicConfig.area_fighting_pos, got)
            elif UserConfig.find_enemy_strategy == 3 and DynamicConfig.area_fighting_pos != 0:
                self.strategy_diagonal(DynamicConfig.area_fighting_pos, got)
            elif UserConfig.find_enemy_strategy == 4 \
                    and hasattr(DynamicConfig, "finder_path") \
                    and DynamicConfig.finder_path != [] \
                    and DynamicConfig.finder_path != 0 \
                    and DynamicConfig.finder_path is not None:
                self.strategy_finder_path(got)
            elif UserConfig.find_enemy_strategy == 999 and DynamicConfig.area_fighting_pos != 0:
                rand = random.randint(0, 1)
                if rand == 0:
                    self.strategy_random(got)
                elif rand == 1:
                    self.strategy_circle_involute(DynamicConfig.area_fighting_pos, got)
                elif rand == 2:
                    self.strategy_square_involute(DynamicConfig.area_fighting_pos, got)
                elif rand == 3:
                    self.strategy_random(got)
            else:
                self.strategy_random(got)

            self.move_count = self.move_count + 1

    # 随机寻怪策略
    def strategy_random(self, got):
        step = UserConfig.move_step if UserConfig.move_step > 0 else random.randint(1, 3)
        if self.move_count % step == 0 and got.value == 0:  # 没怪换角度
            i = random.randint(0, 2)
            self.control.driver.turn_left() if i == 0 else self.control.driver.turn_right()
            # self.control.driver.tap_key("tab")
        else:
            right_click_pos = PixelData.get_another_resolution_point(SysConfig.move_click_pos).confoundPoint(UserConfig.point_confound_rang)
            if UserConfig.find_enemy_move_type == 0 and got.value == 0:
                self.control.driver.move_click_right(right_click_pos, 1)  # x向前走两步
                # self.control.driver.tap_key("tab")
            else:
                start = time.time()
                tick = 0
                self.control.driver.tap_key_up("w")
                self.control.driver.tap_key_down("w")
                while tick < UserConfig.move_step * 3 and not Target().isEnemy(self.player.getLevel()):
                    # self.control.driver.tap_key("tab")
                    if got.value == 0:
                        time.sleep(random.uniform(1.0, 3.0))
                    if got.value == 0:
                        self.random_behavior()
                    if got.value == 0:
                        self.control.driver.turn_random()
                    tick = time.time() - start
                self.control.driver.tap_key_up("w")

            if random.randint(0, 2) == 1:
                self.control.driver.tap_str(" ")  # 空格是跳

    # 圆形渐开线寻怪策略（适合比较方正的区域）
    def strategy_circle_involute(self, area, got):
        from lib.struct.InvoluteLine import InvoluteLine
        from lib.navigation.PathFinding import Pathfinding
        c = InvoluteLine(area)
        pathfinding = Pathfinding(self.control, self.player)
        target = c.get_circle_next_point(pathfinding.getNowPos(), 1, 1)
        if got.value == 0:
            pathfinding.walk(targetPos=target, last=2, combat_exit=True)

    # 方形渐开线寻怪策略（适合比较方正的区域）
    def strategy_square_involute(self, area, got):
        from lib.struct.InvoluteLine import InvoluteLine
        from lib.navigation.PathFinding import Pathfinding
        s = InvoluteLine(area)
        pathfinding = Pathfinding(self.control, self.player)
        target = s.get_square_next_point(pathfinding.getNowPos(), 1)
        if got.value == 0:
            pathfinding.walk(targetPos=target, last=2, combat_exit=True)

    # 对角线寻怪策略（适合狭长区域）
    def strategy_diagonal(self, area, got):
        from lib.struct.DiagonalLine import DiagonalLine
        from lib.navigation.PathFinding import Pathfinding
        d = DiagonalLine(area, 1)
        pathfinding = Pathfinding(self.control, self.player)
        target = d.get_next_point(pathfinding.getNowPos(), int(d.get_len()))
        if not target:
            target = d.switch_line().get_center_ponit()  # 获取另一条对角线的中点
        if got.value == 0:
            pathfinding.walk(targetPos=target, last=2, combat_exit=True)

    # 路点寻怪策略
    def strategy_finder_path(self, got):
        from lib.navigation.StragegyFinderpath import StrageyFinderpath
        s = StrageyFinderpath(self.control, self.player)
        near_pos = s.get_nearst_pos()
        print("最近的路点：")
        print(near_pos.toString())
        checkMount = True
        if hasattr(UserConfig,"use_name_finder") and UserConfig.use_name_finder:
            checkMount = False
        s.walk(targetPos=near_pos, sleep=0.3, combat_exit=True, checkMount=checkMount,targetIsEnemy_exit=True)

        count = 0
        turn_degree = 30
        turn_time = 2 / 360 * turn_degree
        while count < 360 / turn_degree and not Target().isEnemy(self.player.getLevel()):
            self.control.driver.turn_right(turn_time)
            time.sleep(0.3)
            count = count + 1
        if got.value == 0:
            next_pos = s.get_next_pos()
            print("下一个路点：")
            print(next_pos.toString())
            s.walk(targetPos=next_pos, sleep=0.3, combat_exit=True, checkMount=checkMount,targetIsEnemy_exit=True)

    # 清除目标宏
    def clear_target(self):
        self.spell.castSpell(24, 0.5)

    # 转身
    def turn_back(self):
        self.clear_target()
        self.control.driver.turn_right(1)  # 1秒180度

    # 拾取
    def loot(self):
        # from lib.NameFinder.NpcNameFinder import NpcNameFinder
        # finder = NpcNameFinder(needCpture=False)
        # finder.circleLoot(1)
        # print("使用圆圈方式拾取")

        self.control.driver.tap_key(";")
        targetStatus = Target().getStatus()
        # 如果上一个目标没有死亡，那说明这个目标有问题
        if targetStatus["dead"] == 0:
            self.clear_target()
            return False
        self.control.driver.tap_key("'", 1.5)
        print("使用上一个目标方式拾取")

        return True

    # 剥皮
    def baopi(self):
        self.control.driver.tap_key(";")
        targetStatus = Target().getStatus()
        # 如果上一个目标没有死亡，那说明这个目标有问题
        if targetStatus["dead"] == 0:
            self.clear_target()
            return False

        self.control.driver.tap_key("'", 3.2)
        return True

    # 随机行为
    def random_behavior(self):
        r = random.randint(0, 2)
        if r == 0:
            self.control.driver.tap_key_down("a")
            self.control.driver.tap_str(" ")
            time.sleep(random.uniform(0.5, 1.5))
            self.control.driver.tap_key_up("a")
        elif r == 2:
            self.control.driver.tap_key_down("d")
            self.control.driver.tap_str(" ")
            time.sleep(random.uniform(0.5, 1.5))
            self.control.driver.tap_key_up("d")
