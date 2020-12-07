# -*- coding:utf8 -*-

import sys
import os

sys.path.append(os.getcwd())
import multiprocessing
import lib
import time
import random
from lib.tools.threadingFunc import *


# C_QuestLog.GetQuestInfo(questId)

# 交任务宏
# /script SelectGossipAvailableQuest(1)
# /script CompleteQuest()
# /script GetQuestReward(1)

# /click GossipTitleButton1
# /click StaticPopup1Button1
# /click QuestFrameCompleteButton
# /click QuestFrameCompleteQuestButton # 确认弹窗
# /script AcceptQuest()

# 代表一个希利苏斯跑战地声望的玩家
class Silithus_reputation_player(lib.Player):
    jie_npc = "唤风者卡尔东"
    jiao_npc = "布莱卡维尔上尉"
    jiao_npc_part = "布莱"
    chong = "佐拉混合兽"
    dwarf_pos = lib.CoordiPoint(32.8222, 52.5358)  # 交任务的矮子的坐标，使用地图坐标
    counter = 0  # 计数器

    def __init__(self, control: lib.Control, spell: lib.Spell, p=None):
        lib.Player.__init__(self)
        self.control = control
        self.spell = spell
        self.level = self.getLevel()
        self.name = self.getName()
        self.p = p
        self.hander = open("tmp/logs/" + self.getFormatTime(False) + "_silithus_reputation_player_" + self.name + ".log", 'a+')

    # 上马(马必须在23号slot)
    def mounted(self):
        s = self.getStatus()
        if s['combat'] == 0 and s['mounted'] == 0 and s['dead'] == 0:
            self.spell.castSpell(23)
            time.sleep(3)

    # 下马(马必须在23号slot)
    def unmounted(self):
        if self.getStatus()['mounted'] == 1:
            self.spell.castSpell(23)
            time.sleep(0.3)

    # 寻路之前的准备
    def prepare_to_go(self):
        self.control.driver.turn_right(1)  # 转身

    # 协助npc
    def help_npc(self):
        pass

    # 寻路封装
    def __inner_walk(self, t):
        ret = False
        start = time.time()
        navigator = lib.ChoicePathFinding(control=self.control, player=self, checkMount=True, type='p')
        while not ret:
            if time.time() - start > 600:
                sendmail(UserConfig.email, self.name + " walk more than 600", "", img=self.screenshot("walk_more_than_600"))
            if self.getStatus()['dead'] == 1:
                lib.GraveRun(self.control, self).grave_run()
            ret = navigator.to_area_run() if t == 'goto' else navigator.to_repair_run()

    # 选接npc（卡尔东）封装，在循环里是避免出现意外，比如npc挂了
    def __inner_select_jie(self):
        while True:
            if self.getStatus()['dead'] == 1:
                lib.GraveRun(self.control, self).grave_run()
            if lib.Target().getName() != self.jie_npc:
                self.spell.castSpell(14)
                continue
            break

    # 选交npc（矮子） 封装
    def __inner_select_jiao(self):
        self.spell.castSpell(15)

    # 签字
    def __inner_sign(self):
        if self.getStatus()['need_sign_xlss_letter'] == 1 and self.spell.canCast(13, inRange=False):
            self.unmounted()
            time.sleep(0.5)
            self.spell.castSpell(13, 0.5)

    # 任务是否完成
    def __done(self):
        return True if self.getStatus()['xlss_quest_complete'] == 1 else False

    # 死亡检测
    def __death_check(self):
        if self.getStatus()['dead'] == 1:
            sendmail(UserConfig.email, self.name + " die ", "", img=self.screenshot("xlss_queste_" + str(self.counter)))
            lib.GraveRun(self.control, self).grave_run()

    # 疯狗模式专用，实时的走到矮子位置，避免交任务走路浪费时间
    def _mad_dog_walk(self):
        self.__inner_select_jiao()
        if lib.Target().getName().find(self.jiao_npc_part) != -1:
            npc_status = lib.Target().getStatus()
            if npc_status['combat'] == 0 and npc_status['dead'] == 0:  # 矮子战斗中
                npc_percent = lib.Target().getLiftPercent()
                self.control.driver.tap_key(16)  # 选中目标的目标 targettarget
                if lib.Target().getName() == self.chong:
                    chong_status = lib.Target().getStatus()
                    chong_percent = lib.Target().getLiftPercent()

                    # 当矮子血量大于20% 并且 虫子血量小于5%时，说明虫子马上要挂，矮子不会挂，那么提前走到矮子位置等交任务
                    if npc_percent > 0.2 and chong_percent < 0.05:
                        self.control.driver.turn_left(0.35)
                        lib.ChoicePathFinding(control=self.control, player=self, checkMount=True, type='p').walk_to_last_point(self.dwarf_pos)
                        return True
        return False

    def go(self):
        self.__inner_sign()
        if self.__done():  # 如果任务完成
            self.goback()  # 回要塞找卡尔东交任务
        elif not lib.BagItem().hasItem("准备好的战地任务文件"):  # 没有接任务
            self.goback()  # 回要塞找卡尔东接任务
        else:
            self.goto()  # 去矮子那里

    # 去矮子那里
    def goto(self):
        print("开始goto")
        self.someBodyWihsperMe(self.name)
        self.prepare_to_go()
        self.mounted()
        self.__inner_walk("goto")  # 开始寻路去交任务,这个过程中如果死亡，会自动跑尸继续寻路

        # 到达交任务地点交互循环
        while not self.__done():
            print("进入循环")
            self.someBodyWihsperMe(self.name)
            self.__death_check()
            self.__inner_sign()
            self.__inner_select_jiao()
            self.mounted()

            t = lib.Target()
            print(t.getName())
            if not self.__done() and lib.Target().getName().find(self.jiao_npc_part) != -1:
                print("交互中...")
                self.__inner_select_jiao()
                self.control.driver.tap_key("'")  # 与目标交互接任务
                time.sleep(0.5)
                self.control.driver.tap_str(" ")  # 防卡
                time.sleep(3)

            if self.getLiftPercent() < 0.5:
                print("回复。。。。")
                self.control.driver.tap_key("f1")
                self.unmounted()
                self.not_combat_recover()
                self.combat_recover()

            # 有怪打我先干掉
            if self.howManyAreAttackingMe() > 0:
                print("有怪打我")
                lib.EnemyFinder(control=self.control, player=self).clear_target()
                time.sleep(1)
                if lib.Target().isEnemy(self.level):
                    self.kill_loop(lib.Target())

            # 如果不明原因导致离目的地太远，比如被虫子恐惧了，会导致离矮子太远而无法交任务，尝试回到指定位置
            if not self.__done() and (t.getStatus()['combat'] == 1 or t.getStatus()['dead'] == 1):
                self.__death_check()
                print("归位。。。。。。。。")
                p = self.p  # 为None自动使用动态配置文件repair_path最后一个点，如果觉得不合适，可以自定义一个点，注意这里使用的是CoordiPoint
                lib.ChoicePathFinding(control=self.control, player=self, checkMount=True, type='p').walk_to_last_point(p)

            if not self.__done():
                self.__inner_select_jiao()
                self.help_npc()
            print("结束一次循环")
        print("交任务goto完成过")

    # 去卡尔东那里
    def goback(self):
        print("开始goback")
        self.someBodyWihsperMe(self.name)
        self.mounted()
        self.prepare_to_go()
        self.__inner_walk("goback")  # 开始寻路寻路回营地去接任务,这个过程中如果死亡，会自动跑尸继续寻路
        self.__inner_select_jie()
        self.control.driver.tap_key("'")
        time.sleep(2)
        self.spell.castSpell(22)  # 完成任务宏
        time.sleep(0.5)
        self.control.driver.tap_key("'")  # 与目标交互接任务
        time.sleep(1)
        self.counter = self.counter + 1
        print("接任务gotback完成")
        sendmail(UserConfig.email, self.name + " done " + str(self.counter), "", img=self.screenshot("xlss_queste_" + str(self.counter)))
