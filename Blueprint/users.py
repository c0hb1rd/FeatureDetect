import os

from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from Core.AuthorityManager import RoleManager
from Core.DepartmentManager import DepartmentManager
from Core.PersonManager import PersonManager
from Helper.OtherHelper import errorPage, successPage
from Helper.UnlockHelp import getMemory, refreshMemory, cache
from Helper.UserHelper import getImagePath, isLogin, loginRequired
from config import (
    GET,
    GAP, POST)


users = Blueprint("users", __name__, template_folder="templates")


tmpKey = None
tmpRows = None


@users.route("/login", methods=GAP)
def login():
    if isLogin():
        return redirect("/")
    if request.method == GET:
        return render_template("Views/login.html", title="登录")
    elif request.method == 'POST':
        username = request.form.get("username", 0)
        password = request.form.get("password", 0)
        if username and password != 0:
            session['user'] = username
            return redirect("/")
    return render_template("Views/login.html", title="登录")


@loginRequired
@users.route("/logout", methods=GET)
def logout():
    session.pop('user', True)
    return redirect("/")


@users.route("/", methods=GET)
@loginRequired
def index():
    return render_template("Views/index.html", title="生物特征身份识别统一管理平台", user=session['user'])


@users.route("/user", methods=GET)
@loginRequired
def user():
    global tmpRows, tmpKey
    curPage = int(request.args.get("page", 0))
    isReg = int(request.args.get("isReg", 1))
    count = 15

    key = request.args.get("key", "").strip()
    if key == "":
        data = PersonManager.getAllUserLimit(curPage * count, count, isReg)
        print(data.Err)
        rows = PersonManager.getCount(isReg)
    else:
        data = PersonManager.getUserBySearch(key, curPage * count, count, isReg)
        print(data.Err)
        if key != tmpKey:
            rows = PersonManager.getCount(isReg, key)
            tmpRows = rows
        else:
            rows = tmpRows
    allPage = int(rows / count)
    persons = data.Result
    return render_template("Views/User/user.html", title="人员管理", persons=persons, rows=rows, page=curPage, allPage=allPage,
                           count=count, key=key, isReg=isReg)


@users.route("/user/delete/<uID>", methods=GET)
@loginRequired
def delUser(uID):
    userInfo = PersonManager.getUserValue(uID)
    r = PersonManager.delUser(uID)
    if r.Suc:
        # if userInfo['hasLogo']:
        #     imagePath = getImagePath(userInfo['id'])
        #     os.remove(imagePath)
        refreshMemory()
        title = "操作成功"
        message = "删除人员 " + userInfo['userName'] + " 成功"
        return successPage(title, msg=message, url="/user", parent=False)
    else:
        title = "出错"
        message = "删除人员 " + userInfo['userName'] + " 失败: " + str(r.Err)
        return errorPage(title=title, msg=message)


@users.route("/user/mulDelete", methods=POST)
@loginRequired
def mulDelUser():
    title = None
    uIDs = request.form.get("uIDs", 0)[:-1].split(",")
    print(uIDs)
    userName = ""
    for uID in uIDs:
        userInfo = PersonManager.getUserValue(uID)
        r = PersonManager.delUser(uID)
        if r.Suc:
            if userInfo['userLogo'] is not None:
                imagePath = getImagePath(userInfo['id'])
                os.remove(imagePath)
            title = "操作成功"
            userName += userInfo['userName'] + ", "
        else:
            title = "出错"
            message = "删除人员 " + userInfo['userName'] + " 失败: " + str(r.Err)
            return errorPage(title=title, msg=message, url="/user", parent=False)
    refreshMemory()
    message = "删除人员 " + userName + " 成功"
    return successPage(title=title, msg=message, url="/user", parent=False)


@users.route("/user/mulKind/<uIDs>", methods=GAP)
@loginRequired
def mulKind(uIDs):
    if request.method == 'POST':
        tmpUIDs = uIDs
        uIDs = uIDs[:-1].split(",")
        for uID in uIDs:
            departmentID = request.form.get("departmentID")
            ret = PersonManager.updateUserDepartment(uID, departmentID)

            if not ret.Suc:
                refreshMemory()
                return errorPage(msg=str(ret.Err), url="/user/mulKind/" + tmpUIDs, parent=False)
        refreshMemory()
        return successPage(msg="修改部门成功", url="/user", parent=False)
    elif request.method == 'GET':
        allDep = DepartmentManager.getDepartmentList()
        return render_template("Views/User/mulKind.html", title="分配部门", departments=allDep.Result)
    else:
        return errorPage()


@users.route("/user/edit/<uID>", methods=GAP)
@loginRequired
def editUser(uID):
    if request.method == 'GET':
        r = PersonManager.getUser(uID)
        if r.Suc:
            r.Result[0]['roles'] = [line['id'] for line in PersonManager.getUserRoles(uID)]
            r.Result[0].pop("fv", True)
            r.Result[0].pop("fp", True)
            r.Result[0].pop("iris", True)
            r.Result[0].pop("face", True)
            r.Result[0].pop("userLogo", True)
            allRole = RoleManager().getAll()
            allDep = DepartmentManager.getDepartmentList()
            print(allRole.Result)
            print(r.Result[0])
            return render_template("Views/User/edit.html", title="人员修改", person=r.Result[0], departments=allDep.Result, roles=allRole.Result)
        else:
            return errorPage(title="出错", msg="出错" + str(r.Err), url="/user", parent=False)
    elif request.method == 'POST':
        roleIDs = request.form.getlist("roleIDs")
        params = {
            'userName': request.form.get("userName").strip(),
            'loginName': request.form.get("loginName").strip(),
            'gender':  request.form.get("gender").strip(),
            'departmentID': request.form.get("departmentID").strip(),
            'userID': request.form.get("userID").strip(),
            'rights': request.form.get('rights').strip(),
            'id': uID
        }
        r = PersonManager.updateUser(params)
        if r.Suc:
            ret = PersonManager.delFromMap(uID)
            if ret.Suc:
                for roleID in roleIDs:
                    ret = PersonManager.updataMap(uID, roleID)
                    if not ret.Suc:
                        return errorPage(msg="添加角色时是出错：" + str(ret.Err), url="/user/edit/" + uID, parent=False)
            refreshMemory()
            return successPage(title="修改成功", msg="修改成功", url="/user", parent=False)
        else:
            return errorPage(title="修改失败", msg="修改失败: " + str(r.Err) + "证件号已存在", url="/user", parent=False)
