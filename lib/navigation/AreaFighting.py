# -*- coding:utf8 -*-
import random
import time
from lib.navigation.PathFinding import Pathfinding
from lib.control.Control import Control
from lib.unit.Player import Player
from lib.struct.CoordiPoint import CoordiPoint

# 区域打怪
class AreaFighting(Pathfinding):
    # area_pos: 区域4角坐标。顺序为：左上，右上，左下，右下
    def __init__(self, control: Control, player: Player, area_pos, move_type=0):
        Pathfinding.__init__(self, control=control, player=player)
        self.area_pos = area_pos
        self.hander_area = open("tmp/logs/" + self.getFormatTime(False) + "_areafighting.log", 'a+')
        self.start_pos = self.getNowPos()
        self.move_type = move_type

    # 回到区域内
    def goto_area(self):
        nowPos = self.getNowPos()
        if not AreaFighting.pos_in_area(nowPos,self.area_pos) and self.player.getStatus()['combat'] == 0:
            print(nowPos.toString())
            print("not in area #################################################################################")
            print("not in area #################################################################################", file=self.hander_area)
            from lib.navigation.EnemyFinder import EnemyFinder
            EnemyFinder(self.player,self.control).clear_target() #在区域外选中怪先取消掉，免得走回区域后又跑出来打这个怪
            # 直接走向区域中心,没有多余路点
            self.walk(
                self.__get_center_of_area(),
                move_type=self.move_type,
                sleep=0.3,
                precision=0.3,
                last=3,
                combat_exit=True
            )
            #self.player.not_combat_recover()
            self.player.combat_recover()
        return True

    # 获取区域中心点坐标
    # 计算方法：使用中点公式计算一i条对角线的中点即可
    def __get_center_of_area(self):
        left_top = self.area_pos["leftTop"]
        right_bottom = self.area_pos["rightBottom"]
        center = [(left_top[0] + right_bottom[0]) / 2, (left_top[1] + right_bottom[1]) / 2]
        print("center:")
        print(center)
        return CoordiPoint(center[0], center[1])

    # 判断给定坐标是否在区域内
    # 向量叉积(顺时针方向)
    # 四边形内的点都在顺时针（逆时针）向量的同一边，即夹角小于90o，向量积同向
    #    a = (B.x - A.x)*(y - A.y) - (B.y - A.y)*(x - A.x);
    #    b = (C.x - B.x)*(y - B.y) - (C.y - B.y)*(x - B.x);
    #    c = (D.x - C.x)*(y - C.y) - (D.y - C.y)*(x - C.x);
    #    d = (A.x - D.x)*(y - D.y) - (A.y - D.y)*(x - D.x);
    @staticmethod
    def pos_in_area(pos: CoordiPoint,area):
        A = CoordiPoint(area["leftTop"][0], area["leftTop"][1])
        B = CoordiPoint(area["rightTop"][0], area["rightTop"][1])
        C = CoordiPoint(area["rightBottom"][0], area["rightBottom"][1])
        D = CoordiPoint(area["leftBottom"][0], area["leftBottom"][1])
        a = (B.x - A.x) * (pos.y - A.y) - (B.y - A.y) * (pos.x - A.x)
        b = (C.x - B.x) * (pos.y - B.y) - (C.y - B.y) * (pos.x - B.x)
        c = (D.x - C.x) * (pos.y - C.y) - (D.y - C.y) * (pos.x - C.x)
        d = (A.x - D.x) * (pos.y - D.y) - (A.y - D.y) * (pos.x - D.x)
        if (a > 0 and b > 0 and c > 0 and d > 0) or (a < 0 and b < 0 and c < 0 and d < 0):
            return True
        return False
