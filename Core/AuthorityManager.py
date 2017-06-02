from .BaseDB import BaseDB


dbConn = BaseDB()


class Role:
    def __init__(self):
        self.id = None
        self.name = None
        self.keyIDs = None
        self.detail = None
        self.insertKeys = ['name', 'detail']
        self.updateKeys = ['name', 'detail']
        self.searchKeys = ['name', 'detail']

    def __dict__(self):
        return {'id': self.id, 'name': self.name, 'detail': self.detail}


class Key:
    def __init__(self):
        self.id = None
        self.detail = None
        self.name = None
        self.controlIDs = None
        self.insertKeys = ['name', 'detail']
        self.updateKeys = ['name', 'detail']
        self.searchKeys = ['name', 'detail']

    def __dict__(self):
        return {'id': self.id, 'name': self.name, 'detail': self.detail}


class Control:
    def __init__(self):
        self.id = None
        self.detail = None
        self.name = None
        self.system = None
        self.flag = None
        self.menuID = None
        self.parentID = None
        self.status = None
        self.type = None
        self.insertKeys = ['name', 'flag', 'system', 'detail', 'menuID', 'parentID', 'status', 'type']
        self.updateKeys = ['name', 'system', 'flag', 'detail']
        self.searchKeys = ['name', 'system', 'flag', 'detail']

    def __dict__(self):
        return {'id': self.id, 'name': self.name, 'system': self.system, 'flag': self.flag, 'detail': self.detail, 'menuID': self.menuID,
                'parentID': self.parentID, 'status':self.status, 'type':self.type}


class BaseManager:

    def __init__(self, table, obj):
        self.table = table
        self.obj = obj

        self.insertKeyTmp = ", ".join(['`' + k + '`' for k in obj.insertKeys])
        self.insertValueTmp = ", ".join(["%(" + k + ")s" for k in obj.insertKeys])

        self.searchTmp = " OR ".join(
            ['`' + k + '`' + " like %(key)s" for k in obj.searchKeys]
        )

        self.updateTmp = ", ".join(['`' + k + '`' + "=%(" + k + ")s" for k in obj.updateKeys])

    def getAll(self, key=None):
        if key is None and key != "":
            sql = '''SELECT * FROM `''' + self.table + '` ORDER BY `id` DESC'
            r = dbConn.select(sql)
        else:
            sql = '''SELECT * FROM `''' + self.table + '` WHERE %s ORDER BY `id` DESC'% self.searchTmp
            r = dbConn.select(sql, {'key': "%" + key + "%"})
        if r.Suc:
            result = []
            if self.table == 'role':
                for line in r.Result:
                    sql = '''SELECT keyID FROM rk_map WHERE roleID = %(id)s''' % {'id': line['id']}
                    ids = [line['keyID'] for line in dbConn.select(sql).Result]
                    line['keys'] = []
                    for objID in ids:
                        print(objID)
                        line['keys'].append(KeyManager().get(objID).Result[0])
                    result.append(line)
                r.Result = result
            elif self.table == 'key':
                for line in r.Result:
                    sql = '''SELECT * FROM kc_map WHERE keyID = %(id)s''' % {'id': line['id']}
                    ids = [line['controlID'] for line in dbConn.select(sql).Result]
                    line['controls'] = []
                    for objID in ids:
                        line['controls'].append(ControlManager().get(objID).Result[0])
                    result.append(line)
                r.Result = result
        return r

    def get(self, objID):
        sql = '''SELECT * FROM `''' + self.table + '''` WHERE `id` = %(objID)s'''
        r = dbConn.select(sql, {'objID': objID})
        if r.Suc:
            result = []
            if self.table == 'role':
                for line in r.Result:
                    sql = '''SELECT keyID FROM rk_map WHERE roleID = %(id)s''' % {'id': line['id']}
                    ids = [line['keyID'] for line in dbConn.select(sql).Result]
                    line['keys'] = []
                    for objID in ids:
                        print(objID)
                        line['keys'].append(KeyManager().get(objID).Result[0])
                    result.append(line)
                r.Result = result
            elif self.table == 'key':
                for line in r.Result:
                    sql = '''SELECT * FROM kc_map WHERE keyID = %(id)s''' % {'id': line['id']}
                    ids = [line['controlID'] for line in dbConn.select(sql).Result]
                    line['controls'] = []
                    for objID in ids:
                        line['controls'].append(ControlManager().get(objID).Result[0])
                    result.append(line)
                r.Result = result
        return r

    def delete(self, objID):
        sql = '''DELETE FROM `''' + self.table + '''` WHERE `id` = %(objID)s'''
        r = dbConn.execute(sql, {'objID': objID})
        return r

    def update(self, params):
        sql = '''UPDATE `''' + self.table + '''` SET %s WHERE %s''' % (self.updateTmp, '`id` = %(id)s')
        r = dbConn.execute(sql, params)
        return r

    def add(self, params):
        sql = '''INSERT INTO `''' + self.table + '''`(%s) VALUES(%s)''' % (self.insertKeyTmp, self.insertValueTmp)
        print(sql % params)
        r = dbConn.insert(sql, params)
        return r


class RoleManager(BaseManager):
    def __init__(self, table='role', obj=Role()):
        super().__init__(table, obj)

    def updateMap(self, keyIDs, objID):
        ret = dbConn.execute('''DELETE FROM rk_map WHERE roleID = %(id)s''', {'id': objID})
        if ret.Suc:
            for kID in keyIDs:
                ret = dbConn.insert('''INSERT INTO rk_map(roleID, keyID) VALUES(%(roleID)s, %(keyID)s)''', {'roleID': objID, 'keyID': kID})
                if not ret.Suc:
                    break
        return ret

    def getAllKeyID(self, objID):
        sql = '''SELECT keyID FROM rk_map WHERE roleID = %(id)s'''
        return [line['keyID'] for line in dbConn.select(sql, {'id': objID}).Result]

    def delFromMap(self, objID):
        sql = '''DELETE FROM rk_map WHERE `roleID` = %(objID)s'''
        ret = dbConn.execute(sql, {'objID': objID})
        if ret.Suc:
            sql = '''DELETE FROM ur_map WHERE `roleID` = %(objID)s'''
            ret = dbConn.execute(sql, {'objID': objID})
        return ret

    def getKeysByRoleID(self, rID):
        sql = '''SELECT keyID FROM rk_map WHERE roleID = %(rID)s'''
        return dbConn.select(sql, {'rID': rID})



class KeyManager(BaseManager):
    def __init__(self, table='key', obj=Key()):
        super().__init__(table, obj)

    def updateMap(self, ctrls, objID):
        ret = dbConn.execute('''DELETE FROM kc_map WHERE keyID = %(id)s''', {'id': objID})
        if ret.Suc:
            for cID in ctrls:
                ret = dbConn.insert('''INSERT INTO kc_map(keyID, controlID) VALUES(%(keyID)s, %(controlID)s)''', {'keyID': objID, 'controlID': cID})
                if not ret.Suc:
                    break
        return ret

    def getAllCtrlID(self, objID):
        sql = '''SELECT controlID FROM kc_map WHERE keyID = %(id)s'''
        return [line['controlID'] for line in dbConn.select(sql, {'id': objID}).Result]

    def delFromMap(self, objID):
        sql = '''DELETE FROM kc_map WHERE `keyID` = %(objID)s'''
        ret = dbConn.execute(sql, {'objID': objID})
        if ret.Suc:
            sql = '''DELETE FROM rk_map WHERE `keyID` = %(objID)s'''
            ret = dbConn.execute(sql, {'objID': objID})
        return ret

    def getCtrlByKeyID(self, kID):
        print(kID)
        sql = '''SELECT controlID FROM kc_map WHERE keyID = %(kID)s'''
        return dbConn.select(sql, {'kID': kID})


class ControlManager(BaseManager):
    def __init__(self, table='control', obj=Control()):
        super().__init__(table, obj)

    def getAllSortBySystem(self):
        allSystem = list(set([line['system'] for line in dbConn.select('''SELECT `system` FROM `''' + self.table + '''` GROUP BY `system`''').Result]))
        result = []
        for system in allSystem:
            data = {
                'system': system,
                'ctrls': dbConn.select('''SELECT * FROM `''' + self.table + '''` WHERE system = %(system)s''', {'system': system}).Result
            }
            result.append(data)
        return result

    def getSortBySystem(self, params):
        # data = {
        #     'menuID': dbConn.select('''SELECT menuID FROM control WHERE system = %(system)s GROUP BY system''', {'system': params['system']}).Result[0]['menuID'],
        #     'menuName': params['system'],
        #     'menuFrecode': ",".join([line['flag'] for line in dbConn.select('''SELECT * FROM `''' + self.table + '''` WHERE system = %(system)s AND id IN %(id)s''',
        #                            {'system': params['system'], 'id': params['id']}).Result])
        # }
        # return data
        sql = '''SELECT * FROM `control` WHERE system = %(system)s AND id = %(id)s'''
        return dbConn.select(sql, params)
