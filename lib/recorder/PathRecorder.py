# -*- coding:utf8 -*-
import time
import threading
import os
from lib.navigation.PathFinding import Pathfinding
from lib.control.Control import Control
from lib.unit.Player import Player
from lib.struct.CoordiPoint import CoordiPoint
from lib.base.Base import Base
from lib.config.SysConfig import SysConfig


# 路点录制器
class PathRecorder(Base):
    def __init__(self, player: Player, control: Control, filename=None, delay=4):
        Base.__init__(self)
        self.player = player
        self.control = control
        self.filename = SysConfig.record_path + filename if filename is not None else SysConfig.record_path + "DynamicConfig.py"
        self.delay = delay

    def start_record(self):
        while True:
            hander = open(SysConfig.record_path + "walk.txt", "a+")
            content = self.inner_record()
            print(content, file=hander)
            hander.close()
            time.sleep(self.delay)

    # 添加一个分叉路节点
    def add_node(self):
        hander = open(self.filename, "a+")
        coordi = self.player.getCoordi()
        print(coordi.toString() + ",node", file=hander)
        hander.close()

    @staticmethod
    def get_coordi_from_file(filename):
        fp = open(SysConfig.record_path + filename, 'r')
        content = fp.read()
        fp.close()
        array = content.split("\n")
        coords = []
        for i in array:
            if i == "":
                continue
            pos = i.split(",")  # 将坐标转换成数组
            coords.append(CoordiPoint(float(pos[0]), float(pos[1])))
        return coords

    ###########################新版录制方式############################

    # 创建文件（有则覆盖）
    def create_file(self):
        hander = open(self.filename, "w+", encoding="utf-8")
        python = "# -*- coding:utf8 -*-\n\n\n"
        #python += "import lib \n\n\n"
        # python += "from run.config.UserConfig import UserConfig \n\n\n"
        python += "class DynamicConfig:\n"
        python += "    map = \"区域所在地图的名称\"\n"
        python += "    level_min = 0 # 建议的区域最小等级\n"
        python += "    level_max = 0 # 建议的区域最大等级\n"
        python += "    mailbox_pos = [0,0] # 填写邮箱坐标\n"
        python += "    fly_npc_name = \"填写飞行管理员名字\"\n"
        python += "    fly_npc_gossip = 1 # 填写飞行管理员选择飞行点对话索引\n"
        python += "    repair_npc_name = \"填写修理员名字\"\n"
        python += "    repair_npc_gossip = 0 # 填写修理员对话选项索引，如果没有对话选项就填0\n"
        python += "    heartstone_npc_name = \"填写旅店老板名字\"\n"
        python += "    memo = \"如果你有什么需要备注的，需要说明的，使用该区域配置有什么需要注意的，请写在这里，比如荒芜之地有2个精英，容易死\"\n"
        python += "    area_fighting_pos = {\"leftTop\": [0, 0], \"rightTop\": [0, 0], \"leftBottom\": [0, 0], \"rightBottom\": [0, 0]} # 区域打怪4角坐标\n"
        python += "    grave_path = []\n"
        python += "    repair_path = []\n"
        python += "    finder_path = []\n"
        print(python, file=hander)
        print("配置文件创建成功，请录制跑尸路径（grave_path）和修理路径(repair_path)，如果需要使用路点寻怪，还需录制寻怪路径(finder_path)")

    # 录制跑尸路点
    def record_grave(self):
        if not os.path.exists(self.filename):
            print("配置文件不存在，请先使用create创建配置文件")
            return
        try:
            python = "grave_path = [\n"
            while True:
                python += self.inner_record()
        except KeyboardInterrupt as e:
            pass
        python += "    ]"
        hander = open(self.filename, "r+", encoding="utf-8")
        content = hander.read()
        hander.close()
        content = content.replace("grave_path = []", python)
        hander = open(self.filename, "w+", encoding="utf-8")
        print(content, file=hander)
        hander.close()
        print("跑尸路点录制完成")

    # 录制自动修理（从修理员到区域中心点）
    def record_repair(self):
        if not os.path.exists(self.filename):
            print("配置文件不存在，请先使用create创建配置文件")
            return
        try:
            python = "repair_path = [\n"
            while True:
                python += self.inner_record()
        except KeyboardInterrupt as e:
            pass
        python += "    ]"
        hander = open(self.filename, "r+", encoding="utf-8")
        content = hander.read()
        hander.close()
        content = content.replace("repair_path = []", python)
        hander = open(self.filename, "w+", encoding="utf-8")
        print(content, file=hander)
        hander.close()
        print("修理路点录制完成")

    def record_finder(self):
        if not os.path.exists(self.filename):
            print("配置文件不存在，请先使用create创建配置文件")
            return
        print(self.inner_record())
        print("寻怪路点录制完成一个，请复制到动态配置文件中")

    def inner_record(self):
        area = self.player.getArea()
        coordi = self.player.getCoordi()
        world = coordi.to_world(area)
        python = "      [" + coordi.toString() + "," + world.toString() + "," + str(self.player.getFacing()) + ",'" + area + "'],\n"
        time.sleep(self.delay)
        return python

    # 将录制数据提交
    def commit(self):
        if not os.path.exists(self.filename):
            print("配置文件不存在，请先使用create创建配置文件")
            return
        from run.record.path_data.DynamicConfig import DynamicConfig
        from lib.db.mysql import Mysql
        import json
        import numpy as np

        sql = "INSERT INTO AreaInfo (level_min,level_max,fly_npc_name,repair_npc_name,heartstone_npc_name,maibox_pos,area_pos,grave_path,reapir_path,`ctime`,`map`,`memo`,fly_npc_gossip,repair_npc_gossip,finder_path) " \
              "VALUES ({a},{b},{c},{d},{e},{f},{g},{h},{i},{j},{k},{l},{m},{n},{o})".format(
            a=DynamicConfig.level_min,
            b=DynamicConfig.level_max,
            c="'" + DynamicConfig.fly_npc_name + "'",
            d="'" + DynamicConfig.repair_npc_name + "'",
            e="'" + DynamicConfig.heartstone_npc_name + "'",
            f="'" + json.dumps(dict(zip([str(x) for x in np.arange(len(DynamicConfig.mailbox_pos))], DynamicConfig.mailbox_pos)),ensure_ascii=False) + "'",
            g="'" + json.dumps(DynamicConfig.area_fighting_pos,ensure_ascii=False) + "'",
            h="'" + json.dumps(dict(zip([str(x) for x in np.arange(len(DynamicConfig.grave_path))], DynamicConfig.grave_path)),ensure_ascii=False) + "'",
            i="'" + json.dumps(dict(zip([str(x) for x in np.arange(len(DynamicConfig.repair_path))], DynamicConfig.repair_path)),ensure_ascii=False) + "'",
            j="'" + self.getFormatTime(True) + "'",
            k="'" + DynamicConfig.map + "'",
            l="'" + DynamicConfig.memo + "'",
            m=DynamicConfig.fly_npc_gossip,
            n=DynamicConfig.repair_npc_gossip,
            o="'" + json.dumps(dict(zip([str(x) for x in np.arange(len(DynamicConfig.finder_path))], DynamicConfig.finder_path)),ensure_ascii=False) + "'",
        )

        #print(sql)
        client = Mysql().getClient()
        cursor = client.cursor()
        try:
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            client.commit()
        except Exception as e:
            # 如果发生错误则回滚
            client.rollback()
            client.close()
            cursor.close()
            print(e)
            print("数据提交失败")
            return

        # 关闭数据库连接
        client.close()
        cursor.close()
        print("数据提交成功")
        return

    # 从数据库拉取数据
    @staticmethod
    def pull(id):
        from lib.db.mysql import Mysql
        import json
        sql = "select * from AreaInfo where id="+str(id)
        client = Mysql().getClient()
        cursor = client.cursor()
        cursor.execute(sql)
        ret = cursor.fetchone()
        cursor.close()
        client.close()
        if ret == None:
            print("没有找到id为="+str(id)+"的数据")
            return

        mailbox_pos = json.loads(ret[10])
        grave_path_dic = json.loads((ret[12]))
        repair_path_dic = json.loads((ret[13]))
        finder_path_dic = json.loads((ret[14]))

        grave_path = "[\n"
        for i in grave_path_dic:
            t = grave_path_dic[i]
            if i == '0':
                grave_path = grave_path + "        ["+str(t[0])+", "+str(t[1])+", "+str(t[2])+", "+str(t[3])+", "+str(t[4])+", '"+t[5]+"'],"
            else:
                grave_path = grave_path + "\n        ["+str(t[0])+", "+str(t[1])+", "+str(t[2])+", "+str(t[3])+", "+str(t[4])+", '"+t[5]+"'],"
        grave_path = grave_path + "\n    ]"

        repair_path = "[\n"
        for i in repair_path_dic:
            t = repair_path_dic[i]
            if i == '0':
                repair_path = repair_path + "        ["+str(t[0])+", "+str(t[1])+", "+str(t[2])+", "+str(t[3])+", "+str(t[4])+", '"+t[5]+"'],"
            else:
                repair_path = repair_path + "\n        ["+str(t[0])+", "+str(t[1])+", "+str(t[2])+", "+str(t[3])+", "+str(t[4])+", '"+t[5]+"'],"
        repair_path = repair_path + "\n    ]"

        findr_path = "[\n"
        for i in finder_path_dic:
            t = finder_path_dic[i]
            if i == '0':
                findr_path = findr_path + "        [" + str(t[0]) + ", " + str(t[1]) + ", " + str(t[2]) + ", " + str(t[3]) + ", " + str(t[4]) + ", '" + t[5] + "'],"
            else:
                findr_path = findr_path + "\n        [" + str(t[0]) + ", " + str(t[1]) + ", " + str(t[2]) + ", " + str(t[3]) + ", " + str(t[4]) + ", '" + t[5] + "'],"
        finder_path = findr_path + "\n    ]"


        hander = open(SysConfig.record_path + "DynamicConfig.py", "w+", encoding="utf-8")
        python = "# -*- coding:utf8 -*-\n\n\n"
        python += "class DynamicConfig:\n"
        python += "    map = \""+ret[1]+"\"\n"
        python += "    level_min = "+str(ret[2])+" # 建议的区域最小等级\n"
        python += "    level_max = "+str(ret[3])+" # 建议的区域最大等级\n"
        python += "    mailbox_pos = ["+str(mailbox_pos['0'])+","+str(mailbox_pos['1'])+"] # 填写邮箱坐标\n"
        python += "    fly_npc_name = \""+ret[4]+"\"\n"
        python += "    fly_npc_gossip = "+str(ret[5])+" # 填写飞行管理员选择飞行点对话索引\n"
        python += "    repair_npc_name = \""+ret[6]+"\"\n"
        python += "    repair_npc_gossip = "+str(ret[7])+" # 填写修理员对话选项索引，如果没有对话选项就填0\n"
        python += "    heartstone_npc_name = \""+ret[8]+"\"\n"
        python += "    memo = \""+ret[9]+"\"\n"
        python += "    area_fighting_pos = "+ret[11]+"# 区域打怪4角坐标\n"
        python += "    grave_path = "+grave_path+"\n"
        python += "    repair_path ="+repair_path+"\n"
        python += "    finder_path ="+finder_path+"\n"
        print(python, file=hander)
        print("动态配置文件生成完成，请检查是否正确！")
