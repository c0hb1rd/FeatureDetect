from Core.DepartmentManager import DepartmentManager


def getIDFromMap(idMap, name):
    for line in idMap:
        if name == line['name']:
            return line['id']


def departmentName(dID):
    if dID != 0:
        r = DepartmentManager.getDepartment(dID)
        if r.Rows > 0:
            return r.Result[0]['name']
        else:
            return ""
    elif dID == 0:
        return '未注册'


def departmentNameToTable(pID, dID):
    if pID != 0:
        r = DepartmentManager.getDepartment(pID)
        if r.Rows > 0:
            return r.Result[0]['name']
        else:
            return ""
    elif pID == 0:
        if DepartmentManager.hasChildren(dID):
            return '根部门'
        else:
            return "无所属层级"
