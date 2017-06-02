from Core.PersonManager import PersonManager
from .BaseDB import BaseDB, DBResult

dbConn = BaseDB()


class Department:
    def __init__(self):
        self.name = None
        self.detail = None
        self.parentID = None


keys = Department().__dict__.keys()
updateKeys = ['name', 'detail', 'parentID']
searchKeys = ['name', 'detail']
keyTmp = ", ".join(['`' + k + '`' for k in keys])
valueTmp = ", ".join(["%(" + k + ")s" for k in keys])
updateTmp = ", ".join(['`' + k + '`' + "=%(" + k + ")s" for k in updateKeys])
searchTmp = " OR ".join(['`' + k + '`' + " like %(key)s" for k in updateKeys if k in searchKeys])


class DepartmentManager:
    @staticmethod
    def getDepartmentList():
        sql = '''SELECT * FROM department WHERE `id` NOT IN (0, 1)'''

        return dbConn.select(sql)

    @staticmethod
    def getDepartment(dID):
        sql = '''SELECT * FROM department WHERE `id`=%(dID)s'''
        return dbConn.select(sql, {'dID': dID})

    @staticmethod
    def addDepartment(params):
        has, msg = DepartmentManager.hasCurrentName(params)
        r = DBResult()
        if has:
            r.Err = msg
            return r
        if DepartmentManager.hasParentName(params):
            r.Err = "存在名称相同的上层机构名"
            return r
        sql = '''INSERT INTO department(%s) VALUES(%s)''' % (keyTmp, valueTmp)
        r = dbConn.insert(sql, params)
        return r

    @staticmethod
    def delDepartment(uID):
        sql = '''DELETE FROM department WHERE `id` = %(uID)s'''
        return dbConn.execute(sql, {'uID': uID})

    @staticmethod
    def updateDepartment(params):
        has, msg = DepartmentManager.hasCurrentName(params, isUpdate=True)
        r = DBResult()
        if has:
            r.Err = msg
            return r
        if DepartmentManager.hasParentName(params):
            r.Err = "存在名称相同的上层机构名"
            return r
        sql = '''UPDATE department SET %s WHERE %s''' % (updateTmp, "`id` = %(id)s")
        return dbConn.execute(sql, params)

    @staticmethod
    def hasChildren(dID):
        sql = '''SELECT * FROM department WHERE parentID = %(dID)s'''
        r = dbConn.select(sql, {'dID': dID})
        return True if r.Rows > 0 else False

    @staticmethod
    def searchList(key):
        sql = '''SELECT * FROM department WHERE %s AND `id` NOT IN (0, 1)''' % searchTmp
        return dbConn.select(sql, {'key': "%" + key + "%"})

    @staticmethod
    def hasCurrentName(params, isUpdate=False):
        # if params['parentID'] == 0 or params['parentID'] == "0":
        #     return False, None
        sql = '''SELECT * FROM department WHERE parentID = %(parentID)s AND `name` = %(name)s'''
        if isUpdate:
            sql += ''' AND id != %(id)s'''
        r = dbConn.select(sql, params)
        if r.Suc:
            if r.Rows == 0:
                return False, None
            return True, "同层级下已有相同的部门名存在"
        return True, r.Err

    @staticmethod
    def getAllParent(dID):
        if dID == 0:
            return []
        result = []
        sql = '''SELECT * FROM department WHERE id = %(dID)s'''
        ret = dbConn.select(sql, {'dID': dID})
        if ret.Rows > 0:
            line = ret.Result[0]
            result.append(line)
            if line['parentID'] != 0:
                result += (DepartmentManager.getAllParent(line['parentID']))
        return result

    @staticmethod
    def hasParentName(params):
        name = params['name']
        parentID = params['parentID']
        result = DepartmentManager.getAllParent(parentID)

        for line in result:
            if name == line['name']:
                return True
        return False

    @staticmethod
    def getDepChildren(dID):
        sql = '''SELECT * FROM department WHERE parentID = %(dID)s'''
        return dbConn.select(sql, {'dID': dID}).Result

    @staticmethod
    def getDepGroup(dID):
        # child = []
        # curDepInfo = DepartmentManager.getDepartment(dID).Result[0]
        # if DepartmentManager.hasChildren(dID):
        #     curChildrens = DepartmentManager.getDepChildren(dID)
        #     for children in curChildrens:
        #          child.append(DepartmentManager.getDepGroup(children['id']))
        #     curDepInfo['children'] = child
        # curDepInfo['members'] = PersonManager.getUserByDep(curDepInfo['id'])
        # return curDepInfo
        childs = []
        members = []
        curDepInfo = DepartmentManager.getDepartment(dID).Result[0]
        if DepartmentManager.hasChildren(dID):
            curChildrens = DepartmentManager.getDepChildren(dID)
            # for children in curChildrens:
            #      child.append(DepartmentManager.getDepGroup(children['id']))
            # curDepInfo['children'] = child
            # curDepInfo['members'] = PersonManager.getUserByDep(curDepInfo['id'])
            for children in curChildrens:
                child, member = DepartmentManager.getDepGroup(children['id'])
                childs.append(child)
                if member:
                    members += member
            curDepInfo['children'] = childs
        # curDepInfo['members'] = PersonManager.getUserByDep(curDepInfo['id'])
        member = PersonManager.getUserByDep(curDepInfo['id'])
        if member:
            members += member
        return curDepInfo, members


    @staticmethod
    def getRootDepartment():
        sql = '''SELECT id, `name` FROM department WHERE parentID = 0 AND id IN (SELECT parentID FROM department)'''
        return dbConn.select(sql).Result

    @staticmethod
    def getAllDepGroup():
        result = []
        for line in DepartmentManager.getRootDepartment():
            result.append(DepartmentManager.getDepGroup(line['id']))
        return result
