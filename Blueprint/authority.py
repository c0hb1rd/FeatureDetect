from flask import Blueprint, request, render_template, jsonify
import xlrd
from flask import url_for

from Helper.AuthorityHelper import formatKind
from Helper.OtherHelper import errorPage, successPage
from Helper.UserHelper import loginRequired
from Core.AuthorityManager import RoleManager, ControlManager, KeyManager

from config import (
    GAP,
    GET,
    POST)

authority = Blueprint("authority", __name__, template_folder="templates")
roleManager = RoleManager()
keyManager = KeyManager()
controlManager = ControlManager()


@authority.route("/authority/<kind>", methods=GET)
@loginRequired
def listAuth(kind):
    page = int(request.args.get("page", 0))
    key = request.args.get("key", "")
    count = 15
    ret = None
    if kind == 'role':
        ret = roleManager.getAll(key)
    elif kind == 'key':
        ret = keyManager.getAll(key)
    elif kind == 'control':
        ret = controlManager.getAll(key)
    if ret and ret.Suc:
        rows = ret.Rows
        allPage = int(rows / count)
        data = ret.Result[page * count: page * count + count]
        return render_template("Views/Authority/list.html", titile="列表", kind=kind, data=data, rows=rows, allPage=allPage, page=page, key=key, count=count)
    return errorPage(msg="出错:" + str(ret.Err))


@authority.route("/authority/<kind>/add", methods=GAP)
@loginRequired
def addAuth(kind):
    if request.method == 'GET':
        return render_template("Views/Authority/add.html", titile="添加", kind=kind)
    elif request.method == 'POST':
        ret = None
        name = request.form.get("name", "")
        detail = request.form.get("detail", "")
        if name == "":
            return errorPage(msg="名称不能为空", url=url_for("authority.addAuth", kind=kind), parent=False)
        params = {'name': name, 'detail': detail}
        if kind == 'role':
            ret = roleManager.add(params)
        elif kind == 'key':
            ret = keyManager.add(params)
        elif kind == 'control':
            system = request.form.get("system", "")
            flag = request.form.get("flag", "")
            print(1)
            if system == "":
                return errorPage(msg="所属系统不能为空", url=url_for("authority.addAuth", kind=kind), parent=False)
            if flag == "":
                return errorPage(msg="标识不能为空", url=url_for("authority.addAuth", kind=kind), parent=False)
            params['system'] = system
            params['flag'] = flag
            ret = controlManager.add(params)
        if ret and ret.Suc:
            return successPage(msg="添加成功", url=url_for("authority.listAuth", kind=kind), parent=False)
        elif ret:
            return errorPage(msg="添加失败:" + "该名称已存在", url=url_for("authority.addAuth", kind=kind), parent=False)
        else:
            return errorPage(msg="添加失败: 数据库操作异常", url=url_for("authority.addAuth", kind=kind), parent=False)


@authority.route("/authority/<kind>/del/<objID>", methods=GET)
@loginRequired
def delAuth(kind, objID):
    url = url_for("authority.listAuth", kind=kind)
    if request.method == 'GET':
        ret = None
        if objID == "" or objID is None or len(objID) == 0:
            return errorPage(msg="未指定删除对象", url=url, parent=False)
        if kind == 'role':
            ret = roleManager.delete(objID)
            if ret.Suc:
                ret = roleManager.delFromMap(objID)
        elif kind == 'key':
            ret = keyManager.delete(objID)
            if ret.Suc:
                ret = keyManager.delFromMap(objID)
        elif kind == 'control':
            ret = controlManager.delete(objID)
        if ret and ret.Suc:
            return successPage(msg="删除成功", url=url, parent=False)
        elif ret:
            return errorPage(msg="删除失败:" + str(ret.Err), url=url, parent=False)
        else:
            return errorPage(msg="删除失败: 数据库操作异常", url=url, parent=False)
    return errorPage(msg="不接受的请求方式", url=url, parent=False)


@authority.route("/authority/<kind>/muldel", methods=POST)
@loginRequired
def mulDelAuth(kind):
    url = url_for("authority.listAuth", kind=kind)
    if request.method == 'POST':
        objIDs = request.form.getlist("objIDs")
        print(objIDs)
        if objIDs == [] or objIDs is None or len(objIDs) == 0:
            return errorPage(msg="未指定删除对象", url=url, parent=False)
        for objID in objIDs:
            ret = None
            if kind == 'role':
                ret = roleManager.delete(objID)
                if ret.Suc:
                    ret = roleManager.delFromMap(objID)
            elif kind == 'key':
                ret = keyManager.delete(objID)
                if ret.Suc:
                    ret = keyManager.delFromMap(objID)
            elif kind == 'control':
                ret = controlManager.delete(objID)
            if ret and ret.Suc:
                continue
            elif ret:
                return errorPage(msg="删除失败:" + str(ret.Err), url=url, parent=False)
            else:
                return errorPage(msg="删除失败: 数据库操作异常", url=url, parent=False)
        return successPage(msg="删除成功", url=url, parent=False)
    return errorPage(msg="不接受的请求方式", url=url, parent=False)


@authority.route("/authority/<kind>/edit/<objID>", methods=GAP)
@loginRequired
def editAuth(kind, objID):
    if request.method == 'GET':
        data = []
        if kind == 'role':
            data = roleManager.get(objID).Result[0]
        elif kind == 'key':
            data = keyManager.get(objID).Result[0]
        elif kind == 'control':
            data = controlManager.get(objID).Result[0]
        return render_template("Views/Authority/edit.html", titile="添加", kind=kind, data=data)
    elif request.method == 'POST':
        urlBack = url_for("authority.listAuth", kind=kind)
        ret = None
        name = request.form.get("name", "")
        if name == "":
            return errorPage(msg="名称不能为空", url=url_for("authority.addAuth", kind=kind), parent=False)
        if objID == "" or objID is None or len(objID) == 0:
            return errorPage(msg="未指定修改对象", url=urlBack, parent=False)
        params = {'name': name, 'id': objID}
        params['detail'] = request.form.get("detail")
        if kind == 'role':
            ret = roleManager.update(params)
        elif kind == 'key':
            ret = keyManager.update(params)
        elif kind == 'control':
            params['system'] = request.form.get("system")
            params['flag'] = request.form.get("flag")
            params['detail'] = request.form.get("detail")
            ret = controlManager.update(params)
        if ret and ret.Suc:
            return successPage(msg="修改成功", url=urlBack, parent=False)
        elif ret:
            print(ret.Err)
            return errorPage(msg="修改失败:" + str(ret.Err), url=request.url, parent=False)
        else:
            return errorPage(msg="修改失败: 数据库操作异常", url=urlBack, parent=False)


@authority.route("/authority/<kind>/import", methods=GAP)
@loginRequired
def importAuth(kind):
    url = url_for("authority.listAuth", kind=kind)
    if request.method == 'GET':
        return render_template("Views/Authority/import.html", kind=kind, title="导入")
    elif request.method == 'POST':
        data = xlrd.open_workbook(file_contents=request.files['file'].read())
        table = data.sheets()[0]
        idMap = []
        for i in range(1, table.nrows):
            row = table.row_values(i)
            if len(row) < 2:
                del data
                return errorPage(msg="表格格式错误", url=request.url, parent=False)
            name = row[0]
            detail = row[1]
            params = {
                'name': name,
                'detail': detail
            }
            if kind == 'role':
                if len(row) != 2:
                    del data
                    return errorPage(msg="表格格式错误", url=request.url, parent=False)
                ret = roleManager.add(params)
            elif kind == 'control':
                if len(row) != 7:
                    del data
                    return errorPage(msg="表格格式错误", url=request.url, parent=False)
                params['menuID'] = row[0]
                params['name'] = row[1]
                params['detail'] = row[2]
                params['flag'] = row[3]
                params['parentID'] = row[4]
                params['status'] = row[5]
                params['type'] = row[6]
                params['system'] = "生物识别演示系统"
                ret = controlManager.add(params)
            elif kind == 'key':
                ret = keyManager.add(params)
            if ret.Suc:
                idMap.append({'id': ret.Result['LAST_INSERT_ID()']})
            else:
                for line in idMap:
                    if kind == 'role':
                        roleManager.delete(line['id'])
                    elif kind == 'control':
                        keyManager.delete(line['id'])
                    elif kind == 'key':
                        controlManager.delete(line['id'])
                del data
                return errorPage(msg="导入" + formatKind(kind) + "出错，表格第%d行:" % (i + 1) + "有可能该名称已存在或者格式有问题", url=request.url, parent=False)
        del data
        return successPage(msg="导入" + formatKind(kind) + "成功", url="/authority/" + kind, parent=False)
    return errorPage(msg="不接受的请求方式", url=url, parent=False)


@authority.route("/authority/<kind>/classify/<objID>", methods=GAP)
@loginRequired
def classifyAuth(kind, objID):
    if request.method == 'GET':
        ret = None
        listData = None
        if kind == 'role':
            ret = roleManager.get(objID)
            listData = keyManager.getAll()
            allID = roleManager.getAllKeyID(objID)
            if ret.Rows > 0:
                ret.Result[0]['keyIDs'] = allID
                ret.Result[0]['keys'] = listData.Result
        elif kind == 'key':
            ret = keyManager.get(objID)
            listData = controlManager.getAllSortBySystem()
            allID = keyManager.getAllCtrlID(objID)
            if ret.Rows > 0:
                ret.Result[0]['ctrlIDs'] = allID
                ret.Result[0]['controls'] = listData
        if ret and ret.Suc:
            if ret.Rows > 0:
                return render_template("Views/Authority/classify.html", kind=kind, data=ret.Result[0])
            else:
                return errorPage(msg="未定位到分配对象", url=url_for("authority.listAuth", kind=kind), parent=False)
        elif ret:
            return errorPage(msg="出错:" + str(ret.Err), url="/authority/%s" % kind, parent=False)
        return errorPage(msg="异常", url="/authority/%s" % kind, parent=False)
    elif request.method == 'POST':
        if kind == 'role':
            keyIDs = request.form.getlist("keyIDs")
            print(keyIDs)
            ret = roleManager.updateMap(keyIDs, objID)
            if ret.Suc:
                return successPage(msg="分配权限成功", url="/authority/" + kind, parent=False)
            return errorPage(msg="分配权限失败:" + str(ret.Err), url="/authority/" + kind, parent=False)
        elif kind == 'key':
            ctrls = request.form.getlist("ctrls")
            ret = keyManager.updateMap(ctrls, objID)
            if ret.Suc:
                return successPage(msg="分配资源成功", url="/authority/" + kind, parent=False)
            return errorPage(msg="分配资源失败:" + str(ret.Err), url="/authority/" + kind, parent=False)
    return errorPage(msg="不接受的请求方式", url=url_for("authority.listAuth", kind=kind), parent=False)
