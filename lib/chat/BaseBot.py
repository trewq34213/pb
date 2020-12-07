# -*- coding:utf8 -*-

import time
import abc
import os
import random
from lib.base.Base import Base
from lib.db.mysql import Mysql
from lib.control.Control import Control


class BaseBot(Base):
    starter = ["副本去不？...", "升级挺快啊!...", "我去，还在啊？...", "不想去...", "打怪升级真无聊...", "哈哈肚子都给我笑痛...", "你打过克苏恩么...？", "心情不好...", "吃点啥？...", "换号陪我打怪...", "我来啦..."]

    def __init__(self, control: Control):
        Base.__init__(self)
        self.control = control
        self.handler = open("tmp/logs/" + self.getFormatTime(False) + "_basebot.log", 'a+')

    # 和对方打招呼(小队)
    def hello(self, myname, recever):
        msg = self.starter[random.randint(0, len(self.starter) - 2)]

        cmd = "/p"
        self.control.driver.copy_paste_send(cmd)
        time.sleep(0.5)
        self.control.driver.copy_paste_send(msg)

        sql = "insert into chat (`sender`,`recever`,`msg`,`channel`,`type`,`used`,`ctime`) values ({a},{b},{c},{d},{e},{f},{g})" \
            .format(
            a="'" + myname + "'",  # 原消息接收者为消息发送者
            b="'" + recever + "'",  # 原消息发送者为消息接收者
            c="'" + msg + "'",
            d="'p'",
            e=0,
            f=0,
            g="'" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))) + "'"
        )
        Mysql().execute(sql)

    # 和对方打招呼(密语)
    def hello_wisper(self, myname, recever):
        msg = self.starter[random.randint(0, len(self.starter) - 2)]

        cmd = "/w " + recever + " "
        self.control.driver.copy_paste_send(cmd, end_enter=True)
        time.sleep(0.5)
        self.control.driver.copy_paste_send(msg, start_enter=False)

        sql = "insert into chat (`sender`,`recever`,`msg`,`channel`,`type`,`used`,`ctime`) values ({a},{b},{c},{d},{e},{f},{g})" \
            .format(
            a="'" + myname + "'",  # 原消息接收者为消息发送者
            b="'" + recever + "'",  # 原消息发送者为消息接收者
            c="'" + msg + "'",
            d="'w'",
            e=0,
            f=0,
            g="'" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))) + "'"
        )
        Mysql().execute(sql)

    # 发送消息到channle
    def send_msg(self, myname):
        receive_msg_data = self.get_receive_msg(myname)
        if len(receive_msg_data) == 0:
            print("没有待回复消息")
            return

        for data in receive_msg_data:
            reply_msg = self.get_reply_msg(data)
            channel = data[4]

            cmd = ""
            if channel == 'p':
                cmd = "/p"
            elif channel == 'w':
                cmd = "/w " + data[1] + " "

            # 选频道
            if cmd is not "":
                self.control.driver.copy_paste_send(cmd, end_enter=True)
                time.sleep(0.1)

            # 发消息
            if cmd == '/p':
                self.control.driver.copy_paste_send(reply_msg)
            else:
                self.control.driver.copy_paste_send(reply_msg, start_enter=False)

            # 将被回复消息的used更新为1
            sql = "update chat set used=1 where id={a}".format(a=data[0])
            Mysql().execute(sql)
            return True  # 一次只说一句

    # 获取最近一条未回复的消息
    def get_receive_msg(self, recever):
        sql = "select * from chat where used=0 and recever='" + recever + "' order by id desc"
        client = Mysql().getClient()
        cursor = client.cursor()
        cursor.execute(sql)
        msg = cursor.fetchall()
        client.close()
        cursor.close()
        return msg

    # 根据收到消息，调用机器人生成一条回复消息，并写入表中
    def get_reply_msg(self, receive_msg):
        reply_content = self.httpPost(receive_msg[3], receive_msg[0])  # 回复消息的内容
        sql = "insert into chat (`sender`,`recever`,`msg`,`channel`,`type`,`used`,`ctime`) values ({a},{b},{c},{d},{e},{f},{g})" \
            .format(
            a="'" + receive_msg[2] + "'",  # 原消息接收者为消息发送者
            b="'" + receive_msg[1] + "'",  # 原消息发送者为消息接收者
            c="'" + reply_content + "'",
            d="'" + receive_msg[4] + "'",
            e=0,
            f=0,
            g="'" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))) + "'"
        )
        Mysql().execute(sql)
        return reply_content

    @abc.abstractmethod
    def httpPost(self, msg, id):
        pass
