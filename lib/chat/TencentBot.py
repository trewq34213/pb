# -*- coding:utf8 -*-

import time
import json
import random
from lib.chat.BaseBot import BaseBot
from lib.control.Control import Control
import requests
from urllib import parse
import hashlib


#腾讯畅聊机器人
class TencentBot(BaseBot):
    #文档：https://ai.qq.com/doc/nlpchat.shtml
    App_ID = "your app id"
    App_Key = "your app key"
    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat"

    def __init__(self, control: Control):
        BaseBot.__init__(self,control)
        self.handler = open("tmp/logs/" + self.getFormatTime(False) + "_tencentbot.log", 'a+')


    def httpPost(self, msg,id):
        try:
            params = {
                "app_id": self.App_ID,
                "nonce_str": self.ranstr(32),
                "question": msg,
                "session": id,
                "time_stamp": int(time.time()),
            }

            sign = self.__sign(params)
            params["sign"] = sign
            if "app_key" in params.keys():
                del(params['app_key'])

            response = requests.post(self.url,params,30)
            j = response.json()
            print(j, file=self.handler)
            if j.get("ret") == 0:
                return j.get("data").get("answer")
            else:
                return self.starter[random.randint(0,len(self.starter) - 1)]
        except Exception as e:
            print(e, file=self.handler)
            return self.starter[random.randint(0,len(self.starter) - 1)]

    #接口签名
    def __sign(self,p):
        p['app_key'] = self.App_Key
        url = parse.urlencode(p,encoding="utf-8").encode("utf-8")
        return  hashlib.md5(url).hexdigest().upper()

    #生成随机数
    def ranstr(self,num):
        #H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        H = 'abcdef0123456789'

        salt = ''
        for i in range(num):
            salt += random.choice(H)

        return salt

