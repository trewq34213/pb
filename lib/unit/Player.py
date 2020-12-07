# -*- coding:utf8 -*-
import time
from lib.unit.Unit import Unit
from lib.unit.Party import Party
from lib.pixel.PixelData import PixelData
from lib.config.SysConfig import SysConfig
from lib.struct.CoordiPoint import CoordiPoint
from lib.control.Control import Control

# 代表玩家
class Player(Unit):
    whisper = 0
    def __init__(self):
        Unit.__init__(self)

    # 获取玩家名称（70-80）
    def getName(self):
        return PixelData.get_points_string(SysConfig.pixelIndex["playerName"][0], SysConfig.pixelIndex["playerName"][1])

    # 获取玩家职业
    def getClass(self):
        data = PixelData.getPointByIndex(SysConfig.pixelIndex["playerClass"]).getInt()
        if data > len(SysConfig.className):
            return "未知"
        return SysConfig.className[data]

    # 获取玩家坐标
    def getCoordi(self):
        xPoint = PixelData.getPointByIndex(SysConfig.pixelIndex["xCoordi"])
        yPoint = PixelData.getPointByIndex(SysConfig.pixelIndex["yCoordi"])
        x = xPoint.getFloat(10000)
        y = yPoint.getFloat(10000)
        return CoordiPoint(x, y)

    # 获取玩家世界坐标
    def getWorldCoodi(self):
        return self.getCoordi().to_world(self.getArea())

    # 获取玩家朝向弧度
    def getFacing(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["facing"])
        return point.getFloat(100000)

    # 获取尸体坐标，返回0,0表示没有死
    def getCropsCoordi(self):
        xPoint = PixelData.getPointByIndex(SysConfig.pixelIndex["xCorpse"])
        yPoint = PixelData.getPointByIndex(SysConfig.pixelIndex["yCorpse"])
        x = xPoint.getFloat(10000)
        y = yPoint.getFloat(10000)
        return CoordiPoint(x, y)

    # 玩家最大生命值
    def getMaxLife(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["playerMaxLife"])
        return point.getInt()

    # 当前生命值
    def getCurrentLife(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["playerCurrentLife"])
        return point.getInt()

    # 玩家最大魔法（怒气）值
    def getMaxMana(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["playerMaxMana"])
        return point.getInt()

    # 玩家当前魔法（怒气）值
    def getCurrentMana(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["playerCurrentMana"])
        return point.getInt()

    # 等级
    def getLevel(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["playerLevel"])
        return point.getInt()

    # 所在区域
    def getArea(self):
        return PixelData.get_points_string(SysConfig.pixelIndex["area"][0], SysConfig.pixelIndex["area"][1])

    # 姿态
    def getShapeForm(self):
        return PixelData.getPointByIndex(SysConfig.pixelIndex["shapeForm"]).getInt()

    # 获取各种状态
    def getStatus(self):
        bools = PixelData.get_point_bools(SysConfig.pixelIndex["playerStatus"], 23)
        return {"dead": bools[0],
                "is_ghost": bools[1],
                "combat": bools[2],
                "ourtdoor": bools[3],
                "casting": bools[4], #施法
                "channeled": bools[5], # 引导
                # "interrupt ": bools[6], #是否可以打断
                "in_party ": bools[7],
                "in_raid ": bools[8],
                "xlss_quest_complete": bools[9],
                "mounted": bools[10],
                "need_sign_xlss_letter": bools[12],
                "need_blue_bottom": bools[13],
                "need_red_bottom": bools[14],
                "need_cookie": bools[15],
                "need_water": bools[16],
                "need_food": bools[17],
                "need_gem": bools[18],
                "need_bandage": bools[19],
                "need_repair": bools[20],
                "flying": bools[21],
                "talent": bools[22],
                }

    # 是否有某个buff
    # 支持的buff在 Sysconfig的playerBuffs里面
    def hasBuff(self, buffName):
        keys = SysConfig.playerBuffs.keys()
        if buffName not in keys:
            return False
        b = PixelData.get_point_bools(SysConfig.pixelIndex["playerBuffs"], 23)

        if b[SysConfig.playerBuffs[buffName]] == 1:
            return True
        return False

    # 是否有摸个debuff
    # 支持的debuff在Sysconfig的playerDebuffs里面
    def hasDebuff(self, name):
        keys = SysConfig.playerDebuffs.keys()
        if name not in keys:
            return False
        b = PixelData.get_point_bools(SysConfig.pixelIndex["playerDebuffs"], 23)

        if b[SysConfig.playerDebuffs[name]] == 1:
            return True
        return False

    # 金币
    def getGold(self):
        point15 = PixelData.getPointByIndex(SysConfig.pixelIndex["gold1"])
        point16 = PixelData.getPointByIndex(SysConfig.pixelIndex["gold2"])
        num = point15.getInt() + point16.getInt() * 1000000
        gold = int(num / 10000)
        silver = int((num - gold * 10000) / 100)
        copper = num - gold * 10000 - silver * 100
        return {"gold": gold, "silver": silver, "copper": copper}

    # 游戏时长
    def getPlaytime(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["gameTime"])
        num = point.getInt()
        hour = num / 100
        minute = num - hour * 100
        return {"hours": hour, "minute": minute}

    # 多少怪物正在攻击我
    def howManyAreAttackingMe(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["howManyAreAttackingMe"])
        return point.getInt()

    # 有多少人密我
    @staticmethod
    def someBodyWihsperMe(palyerName):
        whisper = PixelData.getPointByIndex(SysConfig.pixelIndex["sombody_whisper_me"]).getInt()
        if whisper > Player.whisper:
            Player.whisper = whisper
            from lib.tools.mail import sendmail
            from lib.base.Base import Base
            from run.config.UserConfig import UserConfig
            sendmail(UserConfig.email, palyerName + "some one whisper to me ", "", Base.screenshot("sombody_whisper_me"))


    # 自动寻路找队友
    def goToParty(self,party:Party,control:Control):
        party_coodri = party.getCoordi()
        if party_coodri.x == 0 and party_coodri.y == 0:
            raise Exception("获取队友："+str(party.i)+"信息失败")
        from lib.navigation.PathFinding import Pathfinding
        pathfinding = Pathfinding(control,self)
        while party.getDisctanc(self) > 0.4:
            pathfinding.walk(targetPos=party.getCoordi(),move_type=0,last=3,combat_exit=True)

    # 非战斗状态的补给
    def not_combat_recover(self):
        print("not_combat_recover：你需要在战斗循环的类中实现该方法，该方法用于在寻路过程中非战斗状态下回复")

    # 战斗状态的补给
    def combat_recover(self):
        print("combat_recover：你需要在战斗循环的类中实现该方法，该方法用于在寻路过程中战斗状态下回复")

    # 修理前的回调
    def before_repair(self):
        print("before_repair：你需要在战斗循环的类中实现该方法，该方法用于在与修理npc对话前执行操作")

    # 开始寻怪前的的回调
    def before_findenemy(self):
        print("before_findenemy：你需要在战斗循环的类中实现该方法，该方法用于在开始寻怪前执行特定操作")

    # 战斗循环
    def kill_loop(self,target):
        print("kill_loop：你需要在战斗循环的类中实现该方法，该方法用于打怪")

    # 上马
    def mounted(self):
        print("mount：你需要在自己实现该方法中实现该方法，该方法用于上马")
        time.sleep(1)
