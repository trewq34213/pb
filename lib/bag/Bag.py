# -*- coding:utf8 -*-
from lib.pixel.PixelData import PixelData
from lib.config.SysConfig import SysConfig
from lib.base.Base import Base


# 代表一个背包
class Bag(Base):
    id = 0  # id 背包编号，0-4，其中0为系统背包，16格子，1-4 为用户背包，从右到左

    def __init__(self, bagId):
        Base.__init__(self)
        self.id = bagId

    # 获取背包格子数量 和 空余数量（如果取下过背包，需要重载插件重新检测）
    def getSlotNumAndFull(self):
        point = PixelData.getPointByIndex(SysConfig.pixelIndex["bagSlot" + str(self.id)])
        num = point.getInt()
        if num == 0:
            return {"slots": 0, "empty": 0}
        slots = int(num / 100)  # 4位数前2位是孔数，后两位是剩余空格
        empty = num % 100
        return {"slots": slots, "empty": empty}

    # 检查所有背包是否都满了
    @staticmethod
    def isAllBagFull():
        full = 0
        for i in range(5):
            tmp = Bag(i).getSlotNumAndFull()
            if tmp['empty'] == 0:
                full = full + 1
        return True if full == 5 else False
