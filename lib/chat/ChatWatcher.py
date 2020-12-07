# -*- coding:utf8 -*-

from lib.base.Base import Base
from lib.db.mysql import Mysql

#通过插件Elephant获取聊天记录写入数据库
class ChatWatcher(Base):
    def __init__(self):
        Base.__init__(self)
        self.handler = open("tmp/logs/" + self.getFormatTime(False) + "_ChatWatcher.log", 'a+')