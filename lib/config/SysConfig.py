# -*- coding:utf8 -*-
from lib.struct.PixelPonit import PixelPoint
import os


class SysConfig:
    move_click_pos = PixelPoint(970, 334)  # 鼠标右键点击移动坐标
    record_path = os.getcwd() + "\\run\\record\\path_data\\"

    className = ["未知", "战士", "骑士", "猎人", "盗贼", "牧师", "死亡骑士", "萨满", "法师", "术士", "武僧", "德鲁伊", "恶魔猎手"]
    pixelIndex = {
        "xCoordi": 1,
        "yCoordi": 2,
        "facing": 3,
        "xCorpse": 4,
        "yCorpse": 5,
        "playerMaxLife": 6,
        "playerCurrentLife": 7,
        "playerMaxMana": 8,
        "playerCurrentMana": 9,
        "playerStatus": 10,
        "playerLevel": 11,
        "undefined": 12,
        "targetMaxLife": 13,
        "targetCurrentLife": 14,
        "gold1": 15,
        "gold2": 16,
        "spellCastable": 17,
        "spellEquipped": 18,
        "spellNotEnoughMana": 19,
        "playerBuffs": 20,
        "playerDebuffs": 21,
        "TargetBuffs": 22,
        "TargetDebuffs": 23,
        "sombody_whisper_me": 24,
        "howManyAreAttackingMe": 25,
        "combatPoints": 26, #连击点数
        "gameTime": 27,
        "gossip": 28,  # npc对话框打开时的可用对话选项 ：0 表示没有对话选项 1 表示有对话选项但没有任务 2 表示只有任务选项 3 表示同时有任务选项和对话选项
        "targetClass": 29,
        "playerClass": 30,
        "canSkin": 31,
        "targetLevel": 32,
        "targetStatus": 33,
        "bagSlot0": 34,
        "bagSlot1": 35,
        "bagSlot2": 36,
        "bagSlot3": 37,
        "bagSlot4": 38,
        "targetUUID": 39,
        # 40 - 54背包物品
        "equipName": 55, # 装备ID
        "equipSlot": 56, # 装备slot
        "shapeForm":57,
        "IsTargetOfTargetPlayerAsNumber":58,
        "findItem":59,
        "targetMaxMana": 62,
        "targetCurrentMana": 63,
        "sellInRange": 64,
        "playerName": [70, 80],
        "targetName": [80, 90],
        "area": [90, 100],
        "party":[100,124],
        "bagItem": 125, #背包是否有某个物品的bit
        # 130 开始是宠物
        "petHealthMax":130,
        "petHealthCurrent":131,
        "petPowerMax":132,
        "petPowerCurrent":133,
        "petStatus":134
    }

    playerBuffs = {
        "奥术智慧": 0,
        "霜甲术": 1,
        "冰甲术": 2,
        "寒冰护体": 3,
        "拯救祝福": 4,
        "荆棘术": 5,
        "命令圣印": 6,
        "正义圣印": 7,
        "十字军圣印": 8,
        "战斗怒吼": 9,
        "进食充分": 10,
        "力量祝福": 11,
        "真言术：韧": 12,
        "野性印记": 13,
        "智慧祝福": 14,
        "牺牲祝福": 15,
        "恶魔皮肤": 17,
        "回春术": 18,
        "真言术：盾": 19,
        "虔诚光环": 20,
        "惩罚光环": 21,
        "心灵之火": 22,
    }

    playerDebuffs = {
        "新近包扎": 0,
        "自律": 1,
        "疲劳": 2,
        "虚弱灵魂": 3,
    }

    TargetBuffs = {
        "奥术智慧": 0,
        "霜甲术": 1,
        "冰甲术": 2,
        "寒冰护体": 3,
        "拯救祝福": 4,
        "荆棘术": 5,
        "命令圣印": 6,
        "正义圣印": 7,
        "十字军圣印": 8,
        "战斗怒吼": 9,
        "进食充分": 10,
        "力量祝福": 11,
        "真言术：韧": 12,
        "野性祝福": 13,
        "智慧祝福": 14,
        "牺牲祝福": 15,
        "鲁莽": 17,
        "盾墙": 18,
        "真言术：盾": 19,
        "光明祝福": 20,
        "惩罚光环": 21,
        "心灵之火": 22,
    }

    TargetDebuffs = {
        "新近包扎": 0,
        "自律": 1,
        "疲劳": 2,
        "虚弱灵魂": 3,
        "挫志怒吼": 4,
        "断筋": 5,
        "撕裂": 6,
        "流血": 7,
        "月火术": 8,
        "精灵之火（野性）": 9,
    }

    BagItems = {
        "准备好的战地任务文件":0,
        "炉石":22,
    }
