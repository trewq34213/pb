# -*- coding:utf8 -*-

import sys
import os

sys.path.append(os.getcwd())
import lib
import threading
import json
import time
from lib.db.mysql import Mysql

# bot状态监测
class Monitor(threading.Thread):
    def __init__(self, player: lib.Player):
        super().__init__()
        self.player = player
        self.target = lib.Target()
        self.bagitem = lib.BagItem(scanItems=True)
        self.mysql = Mysql().getClient()
        self.keyrecorder = lib.KeyRecorder()

    def info(self):
        player = self.player
        target = self.target
        bagitem = self.bagitem

        # 玩家信息
        gold = player.getGold()
        cls = player.getClass()
        shape = player.getShapeForm()
        playtime = player.getPlaytime()
        status = player.getStatus()
        playerInfo = {
            "name": player.getName(),
            "level": player.getLevel(),
            "map": player.getArea(),
            "coordi": player.getCoordi().toString(),
            "life": format(player.getLiftPercent() * 100, '.0f') + "%",
            "mama": format(player.getManaPercent() * 100, '.0f') + "%",
            "gold": str(gold["gold"]) + "金" + str(gold['silver']) + "银" + str(gold['copper']) + "铜",
            # "playtime": str(playtime["hours"]) + "小时",
            "howManyAreAttackingMe": player.howManyAreAttackingMe(),
            "status": status
        }
        if isinstance(player, lib.Silithus_reputation_player):
            playerInfo['战地任务次数'] = player.counter

        if cls == "战士":  # 战士
            if shape == 1:
                playerInfo['姿态'] = "战斗姿态"
            if shape == 2:
                playerInfo['姿态'] = "防御姿态"
            if shape == 3:
                playerInfo['姿态'] = "狂暴姿态"

        if cls == "盗贼":  # 盗贼
            if shape == 1:
                playerInfo['姿态'] = "未潜行"
            if shape == 2:
                playerInfo['姿态'] = "潜行"

        # TODO 小德 牧师

        # 目标信息
        tt = target.IsTargetOfTargetPlayerAsNumber()
        tt_mapper = ["我看我", "我", "无目标", "其它", "我宠物"]
        targetInfo = {
            "UUID": target.getUUID(),
            "name": target.getName(),
            "class": target.getClass(),
            "level": target.getLevel(),
            "touchByOther": target.isTouchByAnoter(),
            "combatPoint": target.getCombatPoints(),
            "targettarget": "未知" if 0 > tt or tt > 4 else tt_mapper[tt],
            "life": format(target.getLiftPercent() * 100, ".0f") + "%",
            "mama": format(target.getManaPercent() * 100, ".0f") + "%",
            "status": target.getStatus()
        }

        ret = {
            "player": playerInfo,
            "t": targetInfo,
            "bag": bagitem.getAllItems()
        }

        return json.dumps(ret, ensure_ascii=False)

    # 键盘按键
    def keys(self):
        return json.dumps(self.keyrecorder.getRecords())

    def insert_or_update(self, info, keys):
        name = self.player.getName()
        cursor = self.mysql.cursor()
        if name is not None and name != "":
            cursor.execute("select id from monitor where `name`=%s", (name))
            res = cursor.fetchone()
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
            if res is not None and res != 0:
                sql = "update monitor set `info`=%s,`keys`=%s,`ctime`=%s where id=%s"
                args = (info, keys, t, res[0])
            else:
                sql = "insert into monitor (`name`,`info`,`keys`,`ctime`) values (%s,%s,%s,%s)"
                args = [name, info, keys, t]
            cursor.execute(sql, args)
            self.mysql.commit()
            cursor.close()
            return True
        return False

    def run(self) -> None:
        while True:
            info = self.info()
            keys = self.keys()
            self.insert_or_update(info, keys)
