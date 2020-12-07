# -*- coding:utf8 -*-

import random
from lib.chat.BaseBot import BaseBot
from lib.control.Control import Control
import requests


# 青云机器人（10分钟内200条）
# http://api.qingyunke.com/
class QingyunBot(BaseBot):
    App_ID = 0
    App_Key = "free"
    url = "http://api.qingyunke.com/api.php"

    def __init__(self, control: Control):
        BaseBot.__init__(self, control)
        self.handler = open("tmp/logs/" + self.getFormatTime(False) + "_qingyun_bot.log", 'a+')

    def httpPost(self, msg, id):
        try:
            response = requests.get(self.url + "?key=" + self.App_Key + "&appid=" + str(self.App_ID) + "&msg=" + msg)
            j = response.json()
            print(j, file=self.handler)
            if j.get("result") == 0:
                return j.get("content")
            else:
                return self.starter[random.randint(0, len(self.starter) - 1)]
        except Exception as e:
            print(e, file=self.handler)
            return self.starter[random.randint(0, len(self.starter) - 1)]
