# -*- coding:utf8 -*-
import sqlite3
import os

class Sqlite3:
    path = os.getcwd() + "\\lib\\db\db.db"

    @staticmethod
    def query(sql,fetch="all",size=0):
        conn = sqlite3.connect(Sqlite3.path)
        cursor = conn.cursor()
        cursor.execute(sql)

        if fetch == "all":
            ret = cursor.fetchall()
        elif fetch == "one":
            ret = cursor.fetchone()
        else:
            ret = cursor.fetchmany(size)

        cursor.close()
        conn.close()
        return ret