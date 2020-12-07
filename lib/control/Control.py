# -*- coding:utf8 -*-
from lib.base.Base import Base


class Control(Base):
    def __init__(self, driver):
        Base.__init__(self)
        self.driver = driver
