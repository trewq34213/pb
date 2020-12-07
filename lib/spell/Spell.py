# -*- coding:utf8 -*-
from lib.base.Base import Base
from lib.pixel.PixelData import PixelData
from lib.control.Control import Control
from run.config.UserConfig import UserConfig
from lib.config.SysConfig import SysConfig
from lib.unit.Target import Target
import math
import time


# 代表技能管理器
class Spell(Base):
    # 13-24 为动作条2，61-72 为左下动作条
    slots = UserConfig.slot_to_key.keys()

    def __init__(self, control: Control):
        Base.__init__(self)
        self.control = control
        from lib.spell.CastingHander import CastingHander
        self.castingHander = CastingHander()

    # 获取slots中技能状态
    # castable 是否冷却完成
    # equipped slot中是否有技能
    # notEnoughMana 是否不满足释放条件，比如魔法不足，怒气能量不足
    def getSatus(self):
        castableBinary = PixelData.getPointByIndex(SysConfig.pixelIndex["spellCastable"]).getInt()
        equippedBinary = PixelData.getPointByIndex(SysConfig.pixelIndex["spellEquipped"]).getInt()
        notEnoughManaBinary = PixelData.getPointByIndex(SysConfig.pixelIndex["spellNotEnoughMana"]).getInt()
        inrangeBinary = PixelData.getPointByIndex(SysConfig.pixelIndex["sellInRange"]).getInt()
        spells = []
        i = 23  # 13-24 和左下动作条61-72一共24个技能
        while i >= 0:
            tmp = {}
            if castableBinary - math.pow(2, i) >= 0:
                tmp['castable'] = True
                castableBinary = castableBinary - math.pow(2, i)
            else:
                tmp['castable'] = False

            if equippedBinary - math.pow(2, i) >= 0:
                tmp['equipped'] = True
                equippedBinary = equippedBinary - math.pow(2, i)
            else:
                tmp['equipped'] = False

            if notEnoughManaBinary - math.pow(2, i) >= 0:
                tmp['notEnoughMana'] = True
                notEnoughManaBinary = notEnoughManaBinary - math.pow(2, i)
            else:
                tmp['notEnoughMana'] = False

            if inrangeBinary - math.pow(2, i) >= 0:
                tmp['inRange'] = True
                inrangeBinary = inrangeBinary - math.pow(2, i)
            else:
                tmp['inRange'] = False

            spells.append(tmp)
            i = i - 1
        spells = spells[::-1]
        ret = {}

        k = 0
        for slot in self.slots:
            ret[slot] = spells[k:k + 1][0]
            k = k + 1
        return ret

    # 检测技能是否可以释放
    def canCast(self, slot, inRange=True):
        if slot < min(self.slots) or slot > max(self.slots):
            return False
        status = self.getSatus()
        if status[slot]['castable'] and status[slot]['equipped'] and not status[slot]['notEnoughMana']:
            if inRange:
                if status[slot]['inRange']:
                    return True
                return False
            return True
        return False

    # 技能释放
    def castSpell(self, slot, delay=0, inSure=True,autoTurn=False):
        if slot < min(self.slots) or slot > max(self.slots):
            raise Exception("slot is not in range")
        while self.castingHander.isCastingOrChanneld():
            print("casting... wait 0.1")
            time.sleep(0.1)
        key = UserConfig.slot_to_key[slot]
        self.control.driver.tap_key(key, delay)
        time.sleep(0.5)

        start = time.time()
        while not self.castingHander.isCastingOrChanneld() and autoTurn and Target().getUUID() != 0 and time.time() - start < 10:
            print("转向敌人")
            self.control.driver.turn_right()
            self.control.driver.tap_key(key, delay)
            time.sleep(0.5)
        if inSure:
            self.castingHander.insureCasting()

    # 检测空位技能是否进入射程
    def inRange(self, slot):
        if slot < min(self.slots) or slot > max(self.slots):
            return False
        status = self.getSatus()
        if status[slot]['inRange']:
            return True
        return False
