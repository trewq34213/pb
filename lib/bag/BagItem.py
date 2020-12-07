import sys
import os

sys.path.append(os.getcwd())
import lib
import time
from lib.pixel.PixelData import PixelData
from lib.config.SysConfig import SysConfig
from lib.base.Base import Base
import threading

items = []


class ItemThread(threading.Thread):
    def run(self):
        print("背包物品检测线程开启,请等带背包物品扫描完成，，，")
        while True:
            slotStand = 0
            for i in range(0, 10, 2):
                index = 40 + i
                bag = int((index - 40) / 2 + 1)
                data = lib.PixelData().getPointByIndex(index).getInt()
                slot = lib.PixelData().getPointByIndex(index + 1).getInt()
                if slotStand == 0:
                    slotStand = slot
                else:
                    if slot != slotStand:
                        continue
                count = int(data / 100000)
                id = data - count * 100000
                # print("--bag:" + str(bag) + "--slot:" + str(slot) + "--id:" + str(id) + "--count:" + str(count))

                has = False
                for item in items[::-1]:
                    if item['id'] == id and item['bag'] == bag and item['slot'] == slot:  # 更新,id必然大于0
                        has = True
                        if item['count'] != count:
                            updateItem = {"id": id, "count": count, "bag": bag, "slot": slot}
                            items.remove(item)
                            items.append(updateItem)
                    if id == 0 and item['bag'] == bag and item['slot'] == slot and item['id'] > 0:  # 说明该位置原来有物品现在没有物品，移除
                        items.remove(item)
                    if 0 < id != item['id'] and item['bag'] == bag and item['slot'] == slot:  # 该位置的物品变了
                        updateItem = {"id": id, "count": count, "bag": bag, "slot": slot}
                        items.remove(item)
                        items.append(updateItem)

                # 没有，加入
                if not has and id > 0 and bag <= 5 and slot <= 20:
                    item = {"id": id, "count": count, "bag": bag, "slot": slot}
                    items.append(item)

                # 去重
                tmpItem = []
                for item in items:
                    if item not in tmpItem:
                        tmpItem.append(item)

                # 数据回items
                items.clear()
                for item in tmpItem:
                    items.append(item)


class BagItem(Base):
    def __init__(self,scanItems = False):
        Base.__init__(self)
        self.scanItems = scanItems
        if scanItems:
            t = ItemThread()
            t.setDaemon(True)
            t.start()

    # @废弃 查找背包是否有某个物品
    # 不通用，每次添加新的物品都需要改插件
    def hasItem(self, itemName):
        keys = SysConfig.BagItems.keys()
        if itemName not in keys:
            return False
        b = PixelData.get_point_bools(SysConfig.pixelIndex["bagItem"], 23)
        if b[SysConfig.BagItems[itemName]] == 1:
            return True
        return False

    # 查找背包是否有某个物品
    # 采用script与插件交互，能兼容所有物品
    def hasItem2(self, itemName,control:lib.Control):
        sql = "select * from items where name='" + itemName + "'"
        ret = lib.Sqlite3().query(sql, 'one')
        if ret is None:
            raise Exception("未在数据库中找到物品:" + itemName)
        id = ret[0]
        from lib.marco.Marco import Marco
        macro = Marco(control)
        macro.findBagItem(id)
        return lib.PixelData.getPointByIndex(SysConfig.pixelIndex["findItem"]).getInt()

    # 获取所有背包物品详细信息
    def getAllItems(self):
        if not self.scanItems:
            return []
        itemsWithInfo = []
        for item in items:
            sql = "select * from items where id=" + str(item['id'])
            ret = lib.Sqlite3().query(sql, 'one')
            if ret is None:
                tmp = {"id": item['id'], "count": item['count'], "bag": item['bag'], "slot": item['slot'], "name": "未知", "qulity": -1, "price": 0}
            else:
                tmp = {"id": item['id'], "count": item['count'], "bag": item['bag'], "slot": item['slot'], "name": ret[1], "qulity": ret[3], "price": ret[4]}
            itemsWithInfo.append(tmp)
        #sortedInfo = sorted(itemsWithInfo, key=lambda r: r['qulity'])
        from operator import itemgetter
        sortedInfo  = sorted(itemsWithInfo, key=itemgetter('qulity'),reverse=True)
        return  sortedInfo

    # 打印信息
    def dumpItems(self):
        a = self.getAllItems()
        print(a)
        print(len(a))
