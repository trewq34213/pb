# -*- coding:utf8 -*-
from lib.base.Base import Base
from lib.control.Control import Control

# 表示一个指令
class Marco(Base):
    def __init__(self, control: Control):
        Base.__init__(self)
        self.control = control

    # 通过宏模板创建一个宏并执行
    def createMarco(self, tplstr, vars):
        if len(vars) == 0:
            marco = tplstr
        else:
            for i in range(len(vars)):
                tplstr = tplstr.replace("${" + str(i) + "}", vars[i])
            marco = tplstr

        if len(marco) > 255:
            print("超过宏最大长度")
            return
        self.control.driver.copy_paste_send(marco)

    # 选中一个目标
    def selectTarget(self, name):
        tpl = "/target ${0}"
        self.createMarco(tpl, [name])

    # 选中目标的第n个对话选项
    def selectGossipOption(self, index):
        tpl = "/script SelectGossipOption(${0})"
        self.createMarco(tpl, [str(index)])

    # 查找背包物品
    def findBagItem(self,id):
        tpl = "/script FIND_ITEM_ID=${0}"
        self.createMarco(tpl,[str(id)])
