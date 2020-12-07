# -*- coding:utf8 -*-

import json
import random
from lib.chat.BaseBot import BaseBot
from lib.control.Control import Control
from urllib import request


# 图灵机器人（一天只有100条。。。）
class TulingBot(BaseBot):
    # api : https://www.kancloud.cn/turing/www-tuling123-com/718227
    # 网站：http://www.tuling123.com/member/robot/2278184/center/frame.jhtml?page=0&child=0
    # 插件：Elephant
    url = "http://openapi.tuling123.com/openapi/api/v2"
    apikey = ['your app id', '']
    secret = ['your secret', '']

    def __init__(self, control: Control):
        BaseBot.__init__(self, control)
        self.handler = open("tmp/logs/" + self.getFormatTime(False) + "_tulingbot.log", 'a+')

    def httpPost(self, msg, id):
        try:
            params = {
                "reqType": 0,  # 输入类型:0-文本(默认)、1-图片、2-音频
                "perception": {
                    "inputText": {
                        "text": msg
                    },
                },
                "userInfo": {
                    "apiKey": self.apikey[0],
                    "userId": id
                }
            }
            params = json.dumps(params)
            params = bytes(params, 'utf8')
            headers = {'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}

            req = request.Request(url=self.url, data=params, headers=headers, method='POST')
            response = request.urlopen(req).read().decode('utf-8')
            print(response, file=self.handler)
            response = json.loads(response)
            response = response['results'][0]['values']['text']
            return response
        except Exception as e:
            print(e, file=self.handler)
            return self.starter[random.randint(0,len(self.starter) - 1)]
