# -*- coding:utf8 -*-

import time
from lib.unit.Unit import Unit
from lib.unit.Party import Party
from lib.pixel.PixelData import PixelData
from lib.config.SysConfig import SysConfig
from lib.struct.CoordiPoint import CoordiPoint
from lib.control.Control import Control

# 宠物
class Pet(Unit):
    def __init__(self):
        Unit.__init__(self)

    def getMaxLife(self):
        return PixelData.getPointByIndex(SysConfig.pixelIndex["petHealthMax"]).getInt()

    def getCurrentLife(self):
        return PixelData.getPointByIndex(SysConfig.pixelIndex["petHealthCurrent"]).getInt()

    def getMaxMana(self):
        return PixelData.getPointByIndex(SysConfig.pixelIndex["petPowerMax"]).getInt()

    def getCurrentMana(self):
        return PixelData.getPointByIndex(SysConfig.pixelIndex["petPowerCurrent"]).getInt()

    def getStatus(self):
        bools = PixelData.get_point_bools(SysConfig.pixelIndex["petStatus"], 23)
        return {
                "exists": bools[0],
                "dead": bools[1],
                "combat": bools[2],
                "visible": bools[3],
                "happy": bools[4],  # 猎人宠物有效 1 = unhappy, 2 = content, 3 = happy
                "slot4": bools[5],
                "slot5": bools[6],
                "slot6": bools[7],
                "slot7": bools[8],
                }
