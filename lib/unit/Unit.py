# -*- coding:utf8 -*-
import abc
import random
import time
from lib.base.Base import Base


# 表示一个游戏内单位
class Unit(Base):

    def __init__(self):
        Base.__init__(self)

    @abc.abstractmethod
    def getMaxLife(self):
        pass

        # 当前生命值

    def getCurrentLife(self):
        pass

    @abc.abstractmethod
    def getMaxMana(self):
        pass

        # 当前生命值

    def getCurrentMana(self):
        pass

    # 获取生命百分比（未正常获取返回0）
    def getLiftPercent(self):
        maxLife = self.getMaxLife()
        if maxLife <= 0:
            return 0
        currentLife = self.getCurrentLife()
        return currentLife / maxLife

    # 获取魔法（怒气）百分比
    def getManaPercent(self):
        maxMana = self.getMaxMana()
        if maxMana <= 0:
            return 1
        currentMana = self.getCurrentMana()
        return currentMana / maxMana
