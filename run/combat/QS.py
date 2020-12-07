# -*- coding:utf8 -*-
import sys
import os

sys.path.append(os.getcwd())
import multiprocessing
import lib
from run.config.UserConfig import UserConfig
import time
import datetime
import random
from lib.tools.threadingFunc import *

# 骑士的战斗文件
class QS(lib.Player):
    def __init__(self, control, spell):
        lib.Player.__init__(self)
        self.control = control
        self.spell = spell
        self.finder = lib.EnemyFinder(self,self.control)

    # 吃喝
    def not_combat_recover(self):
        if self.getStatus()["dead"] == 1:
            return
        if self.getLiftPercent() > 0.8 and self.getLiftPercent() < 1:
            print("圣闪：")
            self.spell.castSpell(63)
        if self.getLiftPercent() < 0.8:
            print("圣光术：")
            self.spell.castSpell(64)
        if self.getStatus()["combat"] == 0 and self.getManaPercent() < 0.4:
            self.spell.castSpell(20, random.uniform(0.5, 1))  # 喝水
            time.sleep(1.5)
            if self.getLiftPercent() < 0.7:
                self.spell.castSpell(21)
            print("吃喝：")
            sec = 0
            while sec < 24 and self.getStatus()["combat"] == 0 and self.getStatus()["dead"] == 0 and self.getManaPercent() < 0.95:
                time.sleep(1)
                sec = sec + 1
            self.control.driver.tap_str(" ")

    # 吃药
    def combat_recover(self):
        if self.getStatus()["dead"] == 1:
            return
        if self.getLiftPercent() < 0.4:  # 血量低于q0%
            if self.spell.canCast(64, inRange=False):
                print("圣光术：")
                self.spell.castSpell(64)
            else:
                self.spell.castSpell(18, 0.5)
                print("吃药(half life)：")
        if self.getLiftPercent() < 0.2:
            self.spell.castSpell(66)  # 无敌
            time.sleep(1.5)
            self.spell.castSpell(72)  # 圣疗

    # 上马(马必须在23号slot)
    def mounted(self):
        s = self.getStatus()
        if s['combat'] == 0 and s['mounted'] == 0 and self.getLevel() >= 40:
            self.spell.castSpell(23)

    # 下马(马必须在23号slot)
    def unmounted(self):
        if self.getStatus()['mounted'] == 1:
            self.spell.castSpell(23)
            time.sleep(0.3)

    # 打怪循环
    def kill_loop(self, target: lib.Target):
        start = time.time()
        playerLevel = self.getLevel()
        while target.isEnemy(playerLevel):  # 因为杀死怪后目标会消失，所以用来判定怪物是否死亡
            if self.getStatus()["dead"] == 1 or self.getStatus()["is_ghost"] == 1:
                return
            if target.getLiftPercent() == 0:
                print("获取目标血量百分比为0", file=hander)
                return
            if self.getStatus()['combat'] == 0:  # 刚进入战斗循环可能还没有进入战斗，乘此机会检测下血量是否需要补给
                self.not_combat_recover()
            self.combat_recover()

            # 如果在战斗状态但是目标的目标不是我，那就是引到其他敌人了
            # 注意：战士使用会有bug，因为冲锋时战士进入战斗，但是被冲锋的怪没有进入战斗
            targetStatus = lib.Target().getStatus()
            if self.getStatus()["combat"] == 1 and targetStatus['combat'] == 0 and targetStatus["target_me"] == 0 and targetStatus['dead'] == 0:
                print("引导怪了,上一个目标ID：" + str(target.ID)+",当前目标ID:"+str(lib.Target().ID),file=hander)
                self.finder.clear_target()
                time.sleep(0.5)

            # if not self.spell.inRange(63):
            self.control.driver.tap_key("'")  # 与目标互动

            if target.getLiftPercent() > 0.95:
                self.control.driver.tap_str(" ")

            if (time.time() - start > UserConfig.time_enemy_full_life) and target.getLiftPercent() > 0.95:  # 选中怪时怪物n秒不掉血，判断为卡地形，转身
                self.control.driver.tap_str(" ")
                self.finder.turn_back()
                print("战斗循环中转身,ID:" + str(target.ID), file=hander)
                break

            if lib.Target().isEnemy(playerLevel):
                if not self.hasBuff("虔诚光环"):
                    self.spell.castSpell(17)
                if lib.Target().getStatus()['combat'] == 1 and lib.Target().getLiftPercent() < 0.9 and not self.hasBuff("命令圣印"):
                    self.spell.castSpell(13)
                self.spell.castSpell(61)
                # if self.spell.canCast(65,inRange=True):
                #     self.spell.castSpell(65)
                print("子循环砍:" + " " + str(datetime.datetime.now()))
        print("战斗循环结束，杀死敌人：ID:" + str(target.ID), file=hander)


if __name__ == '__main__':
    time.sleep(1)
    i = 0
    die_msg_send = full_msg_send = need_red_msg = need_food_msg = need_bandage_msg = need_repair_msg = 0
    driver = lib.Pyinput()
    controlManager = lib.Control(driver)
    spellManager = lib.Spell(control=controlManager)
    player = QS(controlManager, spellManager)
    enemyFinder = lib.EnemyFinder(player, controlManager)
    playerName = player.getName()
    playerLevel = player.getLevel()
    chater = lib.QingyunBot(controlManager)
    if UserConfig.enable_monitor:
        t = lib.Monitor(player)
        t.setDaemon(True)
        t.start()
        print("监控进程启动。。。")

    # from run.web import WebserverThread
    # t = WebserverThread.WebThread(
    #     player=player,
    #     target=lib.Target(),
    #     bagitem=lib.BagItem(control=controlManager, scanItems=True),
    #     host="0.0.0.0",
    #     port=5555)
    # t.setDaemon(True)
    # t.start()

    offline_flag = multiprocessing.Value("d", 0)  # 多进程共享变量 0 标识没有掉线 1 标识掉线

    # checker截图进程
    p1 = multiprocessing.Process(target=checker_screenshot, args=(i, 30,))
    p1.start()

    # GM对话检测进程
    gmtalk_flag = multiprocessing.Value("d", 0)  # 多进程共享变量 0 标识没有掉线 1 标识掉线
    gm = multiprocessing.Process(target=checker_gm, args=(10, gmtalk_flag,))
    gm.start()

    while True:
        loot = 0
        bag_full = lib.Bag.isAllBagFull()
        controlManager.driver.tap_key_up("w")
        status = player.getStatus()

        # 定时关机
        if 0 < UserConfig.shut_time == int(time.localtime(int(time.time())).tm_hour):
            os.system("C:\Windows\System32\taskkill /f /im WowClassic.exe")  # 关机
            time.sleep(60)
            exit(0)

        # 死亡处理
        if status['dead'] == 1 or status['is_ghost'] == 1:
            if die_msg_send == 0:
                sendmail(UserConfig.email, playerName + "died", "", lib.Base.screenshot("die"))
                die_msg_send = 1

            if UserConfig.die_shut == 1:
                os.system("C:\Windows\System32\taskkill /f /im WowClassic.exe")  # 关机
                time.sleep(60)
                exit(0)
            else:
                time.sleep(5)  # 重要，等待释放灵魂
                lib.GraveRun(control=controlManager, player=player).grave_run()
                die_msg_send = 0
                continue

        # 检测背包及补给品情况
        if bag_full and status['combat'] == 0:
            sendmail(UserConfig.email, playerName + "full", "", lib.Base.screenshot("full"))
            lib.AutoRepair(control=controlManager, player=player).repair()  # 自动修理
            continue
        if status['need_red_bottom'] == 1 and need_red_msg == 0:
            sendmail(UserConfig.email, playerName + "need redbottom", "", lib.Base.screenshot("redBottom"))
            need_red_msg = 1
        if status['need_food'] == 1 and need_food_msg == 0:
            sendmail(UserConfig.email, playerName + "need food", "", lib.Base.screenshot("needFood"))
            need_food_msg = 1
        if status['need_bandage'] == 1 and need_bandage_msg == 0:
            sendmail(UserConfig.email, playerName + "nedd bandage", "", lib.Base.screenshot("needBandage"))
            need_bandage_msg = 1
        if status['need_repair'] == 1 and status['combat'] == 0:
            sendmail(UserConfig.email, playerName + "need repair", "", lib.Base.screenshot("need_repair"))
            lib.AutoRepair(control=controlManager, player=player).repair()  # 自动修理
            continue

        # 等级提升恭喜一把
        if i % 5 == 0 and player.getLevel() > playerLevel:
            sendmail(UserConfig.email, playerName + "levelup to " + str(player.getLevel()), "")
            playerLevel = player.getLevel()

        hander = open("tmp/logs/" + date + "_" + playerName + ".log", 'a+')  # 日志写到文件
        print("kill: " + str(i) + " " + str(datetime.datetime.now()) + "\r\n", file=hander)

        target = lib.Target()
        if target.isEnemy(player.getLevel()) is True and player.getStatus()["combat"] == 1:  # 活
            print("多个敌人：" + " " + str(datetime.datetime.now()), file=hander)
            multiprocessing.Process(target=threading_screenshoot, args=(i, "多个敌人",)).start()
            print("进入战斗循环，多个敌人,ID:" + str(target.ID), file=hander)
            player.kill_loop(target)
            i = i + 1

        time.sleep(1)
        player.not_combat_recover()
        player.combat_recover()
        status = player.getStatus()
        if not bag_full and status['combat'] == 0 and loot == 0:
            enemyFinder.loot()  # 捡东西
            loot = 1
            print(str(target.isSkingable()) + "剥皮")
            if status['combat'] == 0:
                time.sleep(0.3)
                enemyFinder.baopi()
        # if not combat(COMBAT_POS):
        #     dd.move_click_right(BODY_POS, 3.5)  # 剥皮
        # food_buff()

        if not player.hasBuff("力量祝福"):  # 智慧祝福
            driver.tap_key("u")

        # if i % 3 == 0 and player.getStatus()['combat'] == 0:
        #     chater.send_msg(playerName)

        target = enemyFinder.find_enemy()
        if target.isEnemy(player.getLevel()):
            player.not_combat_recover()
            player.combat_recover()
            spellManager.castSpell(67)
            print("进入战斗循环:ID:" + str(target.ID))
            player.kill_loop(target)
            i = i + 1
        hander.close()
