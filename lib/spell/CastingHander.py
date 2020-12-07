# -*- coding:utf8 -*-
from lib.base.Base import Base
from lib.unit.Player import Player
import time


# 施法助手
class CastingHander(Base):
    def __init__(self):
        Base.__init__(self)
        self.player = Player()

    def isCastingOrChanneld(self):
        status = self.player.getStatus()
        if status["casting"] == 1 or status["channeled"] == 1:
            return True
        return False

    # 保证施法完成
    def insureCasting(self):
        start = time.time()
        while time.time() - start < 10 and self.isCastingOrChanneld():
            time.sleep(0.1)
