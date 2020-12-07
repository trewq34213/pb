# -*- coding:utf8 -*-
from lib.base.Base import Base
import clr


class NpcNameFinder(Base):
    def __init__(self, needCpture=True):
        Base.__init__(self)
        print(clr.AddReference("lib\\NameFinder\\NpcNameFinder"))
        import NpcNameFinder
        self.dll = NpcNameFinder.Main()
        self.captur = False
        if needCpture:
            self.dll.StartScreenShotThread()
            self.captur = True

    # 鼠标左键点击寻怪
    def findAndClick(self):
        if not self.captur:
            raise Exception("没有启动截取进程，无法进行鼠标点怪")
        self.dll.FindAndClick()

    # 圆形拾取
    def circleLoot(self, count=1):
        c = 0
        while c < count:
            self.dll.Loot()
            c = c + 1
