# -*- coding:utf8 -*-
import math
from lib.unit.Unit import Unit
from lib.pixel.PixelData import PixelData
from lib.config.SysConfig import SysConfig
from run.config.UserConfig import UserConfig


# 代表玩家的目标
class Target(Unit):
    ID = 0

    def __init__(self):
        Unit.__init__(self)
        self.ID = self.getUUID()

    def getUUID(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["targetUUID"])
        return point.getInt()

    def getName(self):
        return PixelData.get_points_string(SysConfig.pixelIndex["targetName"][0], SysConfig.pixelIndex["targetName"][1])

    def getClass(self):
        data = PixelData.getPointByIndex(SysConfig.pixelIndex["targetClass"]).getInt()
        if data > len(SysConfig.className):
            return "未知"
        return SysConfig.className[data]

    def getMaxLife(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["targetMaxLife"])
        return point.getInt()

    def getCurrentLife(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["targetCurrentLife"])
        return point.getInt()

    def getMaxMana(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["targetMaxMana"])
        return point.getInt()

    def getCurrentMana(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["targetCurrentMana"])
        return point.getInt()

    def getLevel(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["targetLevel"])
        return point.getInt()

    def hasBuff(self, buffName):
        keys = SysConfig.TargetBuffs.keys()
        if buffName not in keys:
            return False
        b = PixelData.get_point_bools(SysConfig.pixelIndex["TargetBuffs"], 23)

        if b[SysConfig.TargetBuffs[buffName]] == 1:
            return True
        return False

    def hasDebuff(self,name):
        keys = SysConfig.TargetDebuffs.keys()
        if name not in keys:
            return False
        b = PixelData.get_point_bools(SysConfig.pixelIndex["TargetDebuffs"], 23)

        if b[SysConfig.TargetDebuffs[name]] == 1:
            return True
        return False

    def getStatus(self):
        bools = PixelData.get_point_bools(SysConfig.pixelIndex["targetStatus"], 24)
        status = {
            "combat": bools[0],
            "dead": bools[1],
            "is_enemy": bools[2],
            "can_attack": bools[3],
            "target_me": bools[4],
            "is_elite": bools[5],
            "is_player": bools[6],
            # "casting": bools[7],
            # "channeled": bools[8],
            # "interrupt": bools[9]
        }
        return status

    # 是否可以剥皮
    def isSkingable(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["canSkin"])
        return point.getBool()

    # 被别人摸过的不要,Ture是被别人摸过了
    def isTouchByAnoter(self):
        #enemy_touch_by_other_pos = PixelData.get_another_resolution_point(UserConfig.enemy_touch_by_other_pos)
        x = UserConfig.enemy_touch_by_other_pos.x
        y = UserConfig.enemy_touch_by_other_pos.y
        rgb = PixelData.get_color_RGB(x, y)
        if 170 < rgb[0] < 220:
            return False
        return True

    # 是一个可以攻击的敌人
    def isEnemy(self, palyerLevel):
        if self.ID == 0:
            return False
        status = self.getStatus()
        condition1 = status["can_attack"] \
                     and self.getLevel() - UserConfig.level_height_than_me < palyerLevel < self.getLevel() + UserConfig.level_low_than_me \
                     and status['dead'] == 0

        if UserConfig.attack_elite is False:
            condition1 = condition1 and not status["is_elite"]

        if not condition1:
            return False

        if UserConfig.check_touch_by_other == 1 and self.isTouchByAnoter() is True:
            return False
        return True

    # 获取连击点数
    def getCombatPoints(self):
        return PixelData.getPointByIndex(SysConfig.pixelIndex["combatPoints"]).getInt()

    # 目标的目标是啥
    # 0：自己选中自己；1：目标的目标是我；2：我没有目标或者我的目标无目标 3：目标的目标是别人 4：目标的目标是我的宠物
    def IsTargetOfTargetPlayerAsNumber(self):
        return PixelData.getPointByIndex(SysConfig.pixelIndex["IsTargetOfTargetPlayerAsNumber"]).getInt()
