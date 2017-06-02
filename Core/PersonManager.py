from Helper.TimeHelper import TimeHelper
from Helper.UserHelper import formatSex, formatRights
from .BaseDB import BaseDB


dbConn = BaseDB()


class Person:
    def __init__(self):
        self.recordTime = None
        self.userName = None
        self.userLogo = None
        self.departmentID = None
        self.userID = None
        self.gender = None
        self.fp = None
        self.fv = None
        self.face = None
        self.iris = None
        self.hasLogo = None
        self.fpImg = None
        self.fvImg = None
        self.faceImg = None
        self.irisImg = None


keys = Person().__dict__.keys()
insertKey = ['recordTime', 'userName', 'userLogo', 'gender', 'userID', 'fp', 'fv', 'face', 'iris']
updateKeys = ['userName', 'loginName', 'departmentID', 'gender', 'userID', 'rights']
searchKeys = ['userName', 'loginName', 'userID']
keyTmp = ", ".join(['`' + k + '`' for k in insertKey])
valueTmp = ", ".join(["%(" + k + ")s" for k in insertKey])
searchTmp = " OR ".join(['`' + k + '`' + " like %(key)s" for k in updateKeys if k in searchKeys])
updateTmp = ", ".join(['`' + k + '`' + "=%(" + k + ")s" for k in updateKeys])


class PersonManager:
    @staticmethod
    def getUserList():
        sql = '''SELECT * FROM `user` ORDER BY `id` DESC'''
        return dbConn.select(sql)

    @staticmethod
    def getUser(uID):
        sql = '''SELECT * FROM `user` WHERE `id`=%(uID)s'''
        params = {
            'uID': uID
        }
        return dbConn.select(sql, params)

    @staticmethod
    def addUser(params):
        sql = '''INSERT INTO `user`(%s) VALUES(%s)''' % (keyTmp, valueTmp)
        return dbConn.insert(sql, params)

    @staticmethod
    def delUser(uID):
        sql = '''DELETE FROM `user` WHERE `id` = %(uID)s'''
        ret = dbConn.execute(sql, {'uID': uID})
        if ret.Suc:
            return PersonManager.delFromMap(uID)
        return ret

    @staticmethod
    def delFromMap(uID):
        sql = '''DELETE FROM ur_map WHERE `userID` = %(uID)s'''
        return dbConn.execute(sql, {'uID': uID})

    @staticmethod
    def getAllFeature():
        sql = '''SELECT id, fp, fv, face, iris FROM user'''
        return dbConn.select(sql).Result

    @staticmethod
    def updateUser(params):
        sql = '''UPDATE `user` SET %s WHERE %s''' % (updateTmp, "`id` = %(id)s")
        return dbConn.execute(sql, params)

    @staticmethod
    def updataMap(userID, roleID):
        sql = '''INSERT INTO ur_map(userID, roleID) VALUES(%(userID)s, %(roleID)s)'''
        return dbConn.execute(sql, {'userID': userID, 'roleID': roleID})

    @staticmethod
    def getUserValue(uID):
        sql = '''SELECT * FROM `user` WHERE `id` = %(id)s'''
        return dbConn.getValue(sql, {"id": uID}).Result

    @staticmethod
    def getDepartmentPositionGroup(department):
        sql = '''SELECT `position` FROM `user` WHERE department = %(department)s GROUP BY `position`'''
        r = dbConn.select(sql, {'department': department})
        ret = []
        if r.Rows > 0:
            for line in r.Result:
                users = PersonManager.getDepartmentPositionUser(department, line['position'])
                data = {
                    'users': users,
                    'position': line['position']
                }
                ret.append(data)
        return ret

    @staticmethod
    def getDepartmentPositionUser(department, position):
        sql = '''SELECT userName, gender, userID FROM `user` WHERE department = %(department)s and `position` = %(position)s'''
        r = dbConn.select(sql, {'department': department, 'position': position})
        if r.Rows > 0:
            return r.Result

    @staticmethod
    def getAllDepartment():
        ret = []
        sql = '''SELECT department FROM user GROUP BY department ORDER BY department'''
        r = dbConn.select(sql)
        for line in r.Result:
            data = {}
            department = line['department']
            groups = PersonManager.getDepartmentPositionGroup(department)
            data['department'] = department
            data['groups'] = groups
            ret.append(data)
        return ret

    @staticmethod
    def getDepartmentGroup(department):
        data = {}
        groups = PersonManager.getDepartmentPositionGroup(department)
        data['department'] = department
        data['groups'] = groups
        return data

    @staticmethod
    def getUserBySearch(key, start, end, isReg):
        if isReg == 0:
            sql = '''SELECT `id`, hasLogo, userName, userID, gender, departmentID, loginName, recordTime FROM user WHERE %s AND departmentID = 0 ORDER BY `id` DESC %s''' % (searchTmp, "LIMIT %(start)s, %(end)s")
        else:
            sql = '''SELECT `id`, hasLogo, userName, userID, gender, departmentID, loginName, recordTime FROM user WHERE %s ORDER BY `id` DESC %s''' % (searchTmp, "LIMIT %(start)s, %(end)s")
        r = dbConn.select(sql, {'start': start, 'end': end, 'key': "%" + key + "%"})
        if r.Result:
            result = []
            for line in r.Result:
                from Core.DepartmentManager import DepartmentManager
                line['roles'] = [line['name'] for line in PersonManager.getUserRoles(line['id'])]
                result.append(line)
            r.Result = result
        return r

    @staticmethod
    def getCount(isReg, key=None):
        if key:
            if isReg == 0:
                ret = dbConn.select('''SELECT count(`id`) FROM user WHERE %s AND department = 0 ''' % searchTmp, {'key': key})
            else:
                ret = dbConn.select('''SELECT count(`id`) FROM user WHERE %s ''' % searchTmp,{'key': key})
        else:
            if isReg == 0:
                ret = dbConn.select('''SELECT count(`id`) FROM user WHERE departmentID = 0''')
            else:
                ret = dbConn.select('''SELECT count(`id`) FROM user''')
        if ret.Result:
            return ret.Result[0]['count(`id`)']
        else:
            return 0

    @staticmethod
    def updateUserDepartment(uID, departmentID):
        sql = '''UPDATE user SET departmentID = %(departmentID)s WHERE id = %(uID)s'''
        return dbConn.execute(sql, {'departmentID': departmentID, 'uID': uID})

    @staticmethod
    def resetDepartment(dID):
        sql = '''UPDATE user SET departmentID = 0 WHERE departmentID = %(id)s'''
        return dbConn.execute(sql, {'id': dID})

    @staticmethod
    def getUserByDep(dID):
        sql = '''SELECT userName, `id`, loginName, gender, recordTime, departmentID, hasLogo, userID, rights FROM user WHERE departmentID = %(dID)s'''
        r = dbConn.select(sql, {'dID': dID})
        if r.Result:
            result = []
            for line in r.Result:
                from Core.DepartmentManager import DepartmentManager
                line['recordTime'] = TimeHelper.formatTime(line['recordTime'])
                line['gender'] = formatSex(line['gender'])
                line['department'] = DepartmentManager.getDepartment(line['departmentID']).Result[0]['name']
                line['roles'] = [line['name'] for line in PersonManager.getUserRoles(line['id'])]
                if line['roles']:
                    line['roles'] = "、".join(line['roles'])
                else:
                    line['roles'] = "无"
                line['rights'] = formatRights(line['rights'])
                line.pop("departmentID", True)
                line.pop("roleIDs", True)
                result.append(line)
            r.Result = result
        return r.Result

    @staticmethod
    def getUserRoles(uID):
        sql = 'SELECT roleID FROM ur_map WHERE userID = %(id)s'
        ret = dbConn.select(sql, {'id': uID})
        result = []
        if ret.Rows:
            for line in ret.Result:
                result.append(dbConn.select('''SELECT * FROM role WHERE id = %(roleID)s''', {'roleID': line['roleID']}).Result[0])
        return result

    @staticmethod
    def getAllUserLimit(start, end, isReg):
        if isReg == 0:
            sql = '''SELECT userName, `id`, loginName, gender, recordTime, departmentID, hasLogo, userID, rights FROM user WHERE departmentID = 0 ORDER BY `id` DESC LIMIT %(start)s, %(end)s'''
        else:
            sql = '''SELECT userName, `id`, loginName, gender, recordTime, departmentID, hasLogo, userID, rights FROM user ORDER BY `id` DESC LIMIT %(start)s, %(end)s '''
        r = dbConn.select(sql, {'start': start, 'end': end})
        if r.Result:
            result = []
            for line in r.Result:
                from Core.DepartmentManager import DepartmentManager
                line['roles'] = [line['name'] for line in PersonManager.getUserRoles(line['id'])]
                result.append(line)
            r.Result = result
        return r

    @staticmethod
    def getUserByUserID(userID):
        sql = '''SELECT * FROM `user` WHERE `userID` = %(userID)s'''
        return dbConn.select(sql, {'userID': userID})
