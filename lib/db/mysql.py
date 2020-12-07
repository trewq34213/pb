import pymysql
from lib.base.Base import Base

class Mysql(Base):
    host = "your host"
    port = 3306
    dbanme = "wow"
    user = "remote"
    passwod = "your password"
    client = None

    def __init__(self):
        Base.__init__(self)
        self.client = pymysql.connect(host=self.host, user=self.user, password=self.passwod,
                                      database=self.dbanme, port=self.port,charset="utf8mb4")

    def getClient(self):
        return self.client

    def execute(self,sql,args=None):
        client = self.getClient()
        cursor = client.cursor()
        res = cursor.execute(sql, args)
        client.commit()
        client.close()
        cursor.close()
        return res
