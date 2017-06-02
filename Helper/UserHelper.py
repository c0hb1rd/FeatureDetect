import os
from functools import wraps

from flask import redirect
from flask import session
from flask import url_for



def getImagePath(userID):
    currentPath = os.getcwd()
    imagePath = os.path.join(currentPath, "static", "Image", "Users", str(userID))
    return imagePath


def formatSex(gender):
    if gender == 1:
        sex = '女'
    elif gender == 0:
        sex = '男'
    else:
        sex = '不明'
    return sex


def listUser(users):
    ret = []
    for user in users:
        ret.append(user['userName'])
    return ret


def isLogin():
    if 'user' in session:
        return True
    else:
        return False


def formatRights(rights):
     return "管理员" if rights == 1 else "普通用户"


def formatRoles(roles):
    if roles:
        result = ""
        for role in roles:
            result += role + "、"
        return result
    else:
        return "无"


def loginRequired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('users.login', returnUrl="/"))
        return f(*args, **kwargs)
    return decorated_function
