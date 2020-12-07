# -*- coding:utf8 -*-

import sys
import os

sys.path.append(os.getcwd())
import threading
import json
import lib
from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("info.html")


@app.route('/info', methods=['GET', 'POST'])
def info():
    player = WebThread.player
    target = WebThread.target
    bagitem = WebThread.bagitem

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
        # "shape" : player.getShapeForm(),
        "gold": str(gold["gold"]) + "金" + str(gold['silver']) + "银" + str(gold['copper']) + "铜",
        # "playtime": str(playtime["hours"]) + "小时",
        "howManyAreAttackingMe": player.howManyAreAttackingMe(),
        "status": status
    }
    if isinstance(player,lib.Silithus_reputation_player):
        playerInfo['战地任务次数'] = player.counter

    if cls == "战士": # 战士
        if shape == 1:
            playerInfo['姿态'] = "战斗姿态"
        if shape == 2:
            playerInfo['姿态'] = "防御姿态"
        if shape == 3:
            playerInfo['姿态'] = "狂暴姿态"

    if cls == "盗贼": # 盗贼
        if shape == 1:
            playerInfo['姿态'] = "未潜行"
        if shape == 2:
            playerInfo['姿态'] = "潜行"

    #TODO 小德 牧师


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
        "code": 200,
        "player": playerInfo,
        "t": targetInfo,
        "bag": bagitem.getAllItems()
    }

    return json.dumps(ret, ensure_ascii=False)


@app.route('/keys', methods=['GET'])
def keys():
    from lib.control.KeyRecorder import KeyRecorder
    return {
        "code": 200,
        "records":KeyRecorder().getRecords()
    }

class WebThread(threading.Thread):
    player = None
    target = None
    bagitem = None
    host = "127.0.0.1"
    port = 5555

    def __init__(self, player, target: lib.Target, bagitem: lib.BagItem, host=None, port=None):
        super().__init__()
        WebThread.player = player
        WebThread.target = target
        WebThread.bagitem = bagitem
        if host is not None:
            WebThread.host = host
        if port is not None:
            WebThread.port = port

    def run(self) -> None:
        app.run(host=WebThread.host, port=WebThread.port, ssl_context=(
            "run\web\ca-cert.pem",
            "run\web\ca-key.pem"))
