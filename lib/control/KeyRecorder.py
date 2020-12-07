# -*- coding:utf8 -*-

# -*- coding:utf8 -*-
import time
import random
import threading
from lib.base.Base import Base


# 按键记录器
class KeyRecorder(threading.Thread):
    records = []
    keep = 20  # 保留记录条数

    def __init__(self):
        super().__init__()

    def record(self, key):
        timeArray = time.localtime(int(time.time()))
        self.records.insert(0, time.strftime("%H:%M:%S", timeArray) + " " + key)

    def reduce(self):
        if len(self.records) > self.keep:
            cut = len(self.records) - self.keep
            for i in range(cut):
                self.records.pop()

    def getRecords(self):
        return list(self.records)

    def run(self) -> None:
        while True:
            self.reduce()
            time.sleep(5)
