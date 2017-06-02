import pymysql

from config import (
    DB,
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_CHARSET
)


class DBResult:
    Suc = False
    Result = None
    Err = None
    Rows = None

    def __init__(self):
        pass


class BaseDB:
    def __init__(self):
        self.dbConn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB, charset=DB_CHARSET,
                                      cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.dbConn.cursor()
        self.columns = []

    # Return DBResult
    def select(self, sql, params=None):
        # if self.dbConn is None:
        #     self.dbConn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB, charset=DB_CHARSET,
        #                                   cursorclass=pymysql.cursors.DictCursor)
        #     self.cursor = self.dbConn.cursor()
        r = DBResult()
        try:
            if params is None or len(params) == 0 or type(params) != dict:
                r.Rows = self.cursor.execute(sql)
            else:
                r.Rows = self.cursor.execute(sql, params)
            r.Result = self.cursor.fetchall() if r.Rows != 0 else []
            r.Suc = True
        except Exception as e:
            r.Err = e
        # self.cursor = None
        # if self.dbConn is not None:
        #     self.dbConn.close()
        # self.dbConn = None
        return r

    # Return DBResult
    def execute(self, sql, params=None, close=True):
        # if self.dbConn is None:
        #     self.dbConn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB, charset=DB_CHARSET,
        #                                   cursorclass=pymysql.cursors.DictCursor)
        #     self.cursor = self.dbConn.cursor()
        r = DBResult()
        try:
            if not params:
                r.Rows = self.cursor.execute(sql)
            else:
                r.Rows = self.cursor.execute(sql, params)
            r.Result = self.cursor.fetchall() if r.Rows != 0 else []
            r.Suc = True
            self.dbConn.commit()
        except Exception as e:
            r.Err = e
            self.dbConn.rollback()
        # if close:
        #     self.cursor = None
        #     if self.dbConn is not None:
        #         self.dbConn.close()
        #     self.dbConn = None
        return r

    # Return DBResult
    def insert(self, sql, params=None):
        # if self.dbConn is None:
        #     self.dbConn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB, charset=DB_CHARSET,
        #                                   cursorclass=pymysql.cursors.DictCursor)
        #     self.cursor = self.dbConn.cursor()
        r = self.execute(sql, params, False)
        if not r.Suc:
            r.Result = -1
            return r
        r.Rows = self.cursor.execute("SELECT LAST_INSERT_ID()")
        r.Result = self.cursor.fetchone() if r.Rows != 0 else []

        # self.cursor = None
        # if self.dbConn is not None:
        #     self.dbConn.close()
        # self.dbConn = None
        return r

    # Return DBResult
    def getValue(self, sql, params=None):
        # if self.dbConn is None:
        #     self.dbConn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB, charset=DB_CHARSET,
        #                                   cursorclass=pymysql.cursors.DictCursor)
        #     self.cursor = self.dbConn.cursor()
        r = self.select(sql, params)
        if r.Suc:
            if r.Result:
                r.Result = r.Result[0]
            else:
                r.Result = -1
        return r


class BaseManager:

    def __init__(self, table, obj):
        self.table = table
        self.obj = obj
        self.dbConn = BaseDB().dbConn

        self.insertKeyTmp = ", ".join(['`' + k + '`' for k in obj.insertKeys])
        self.insertValueTmp = ", ".join(["%(" + k + ")s" for k in obj.insertKeys])

        self.searchTmp = " OR ".join(
            ['`' + k + '`' + " like %(key)s" for k in obj.searchKeys]
        )

        self.updateTmp = ", ".join(['`' + k + '`' + "=%(" + k + ")s" for k in obj.updateKeys])

    def getAll(self):
        sql = '''SELECT * FROM %(table)s'''
        r = self.dbConn.select(sql, {'table': self.table})
        return r

    def get(self, objID):
        sql = '''SELECT * FROM %(table)s WHERE `id` = %(objID)s'''
        r = self.dbConn.select(sql, {'table': self.table, 'objID': objID})
        return r

    def delete(self, objID):
        sql = '''DELETE FROM %(table)s WHERE `id` = %(objID)s'''
        r = self.dbConn.execute(sql, {'table': self.table, 'objID': objID})
        return r

    def update(self, params):
        sql = '''UPDATE %s SET %s WHERER %s''' % (self.table, self.updateTmp, '`id` = %(id)s')
        r = self.dbConn.execute(sql, params)
        return r

    def add(self, params):
        sql = '''INSERT INTO %s(%s) VALUES(%s)''' %(self.table, self.insertKeyTmp, self.insertValueTmp)
        r = self.dbConn.insert(sql, params)
        return r
