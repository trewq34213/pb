# -*- coding:utf8 -*-
from lib.base.Base import Base
from lib.struct.Point import Point


#表示一条线段
class Line(Base):
    def __init__(self, start: Point, end: Point):
        super().__init__()
        self.start = start
        self.end = end

    def toString(self):
        print(self.start.toString(),self.end.toString())
