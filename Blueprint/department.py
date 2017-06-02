import json

import xlrd
from flask import Blueprint, request, render_template, jsonify

from Core.DepartmentManager import DepartmentManager
from Core.PersonManager import PersonManager
from Helper.DepartmentHelpler import getIDFromMap
from Helper.OtherHelper import successPage, errorPage
from Helper.UnlockHelp import refreshMemory
from Helper.UserHelper import loginRequired
from config import (
    GAP,
    GET
)

department = Blueprint("department", __name__, template_folder="templates")


@department.route("/department/list", methods=GET)
@loginRequired
def listDep():
    ret = DepartmentManager.getDepartmentList()
    if ret.Suc:
        allRoot = DepartmentManager.getRootDepartment()
        return render_template("Views/department/list.html", title="部门信息", data=ret.Result, rootDep=allRoot)
    else:
        return errorPage(msg=str(ret.Err))


@department.route("/department/list/<dID>", methods=GET)
@loginRequired
def depGroup(dID):
    depGroups, members = DepartmentManager.getDepGroup(dID)
    depGroups['allMembers'] = members
    return json.dumps([depGroups])
    # return json.dumps([DepartmentManager.getDepGroup(dID)])


@department.route("/department/table", methods=GET)
@loginRequired
def tableDep():
    page = int(request.args.get("page", 0))
    key = request.args.get("key", "none")
    count = 15
    if key != "none":
        ret = DepartmentManager.searchList(key)
    else:
        ret = DepartmentManager.getDepartmentList()
    if ret.Suc:
        rows = ret.Rows
        allPage = int(rows / count)
        departments = ret.Result[page * count: page * count + count]
        return render_template("Views/department/table.html", title="部门列表", data=ret.Result, rows=rows, allPage=allPage, page=page, key=key, count=count, departments=departments)
    else:
        return errorPage(msg=str(ret.Err))


@department.route("/department/edit/<dID>", methods=GAP)
@loginRequired
def editDep(dID):
    if request.method == 'GET':
        allDep = DepartmentManager.getDepartmentList()
        d = DepartmentManager.getDepartment(dID)
        return render_template("Views/department/edit.html", title="修改部门", departments=allDep.Result, d=d.Result[0])
    elif request.method == 'POST':
        name = request.form.get('name').strip()
        parentID = int(request.form.get('parentID'))
        detail = request.form.get('detail').strip()
        params = {
            'id': dID,
            'name': name,
            'parentID': parentID,
            'detail': detail
        }
        ret = DepartmentManager.updateDepartment(params)
        if ret.Suc:
            return successPage(msg="修改部门 %s 成功" % name, url="/department/table", parent=False)
        else:
            return errorPage(msg="修改部门 %s 失败：" % name + str(ret.Err), url=request.url, parent=False)

    return errorPage(title='错误请求', msg="错误请求")


@department.route("/department/del/<dID>", methods=GET)
@loginRequired
def delDep(dID):
    dInfo = DepartmentManager.getDepartment(dID)
    if DepartmentManager.hasChildren(dID):
        return errorPage(msg="该部门包含子机构，无法删除", url="/department/table", parent=False)
    else:
        ret = DepartmentManager.delDepartment(dID)
        if ret.Suc:
            PersonManager.resetDepartment(dID)
            refreshMemory()
            return successPage(msg="成功删除 %s 部门" % dInfo.Result[0]['name'], url="/department/table", parent=False)
        else:
            return errorPage(msg="删除出错：" + str(ret.Err), url="/department/table", parent=False)


@department.route("/department/add", methods=GAP)
@loginRequired
def addDep():
    if request.method == 'GET':
        allDep = DepartmentManager.getDepartmentList()
        if allDep.Suc:
            return render_template("Views/department/add.html", title="添加部门", departments=allDep.Result)
        else:
            return errorPage(msg="获取部门列表时出错")
    elif request.method == 'POST':
        name = request.form.get('name', None)
        parentID = int(request.form.get('parentID'))
        detail = request.form.get('detail', None)

        if name is None:
            return errorPage(msg="部门名字不能为空")
        else:
            params = {
                'name': name,
                'parentID': parentID,
                'detail': detail
            }
            ret = DepartmentManager.addDepartment(params)
            if ret.Suc:
                return successPage(msg="添加部门 %s 成功" % name, url="/department/table", parent=False)
            else:
                return errorPage(msg="添加部门 %s 失败:" % name + str(ret.Err), parent=False, url="/department/add")
    return errorPage(title='错误请求', msg="错误请求")


@department.route("/department/import", methods=GAP)
@loginRequired
def importDep():
    if request.method == 'GET':
        allDep = DepartmentManager.getDepartmentList()
        return render_template("Views/department/import.html", title="导入部门", deps=allDep.Result)
    elif request.method == 'POST':
        data = xlrd.open_workbook(file_contents=request.files['file'].read())
        parentID = int(request.form.get('parentID'))
        table = data.sheets()[0]
        idMap = []
        for i in range(1, table.nrows):
            row = table.row_values(i)
            name = row[0]
            detail = row[1]
            parent = row[2]
            params = {'name': name, 'detail': detail, 'parentID': parentID}
            if i == 1 and parentID != 0:
                ret = DepartmentManager.addDepartment(params)
            elif i == 1 and parentID == 0:
                ret = DepartmentManager.addDepartment(params)
            else:
                params['parentID'] = getIDFromMap(idMap, parent)
                ret = DepartmentManager.addDepartment(params)
            if ret.Suc:
                idMap.append({'name': name, 'parentID': parentID, 'id': ret.Result['LAST_INSERT_ID()']})
            else:
                for line in idMap:
                    DepartmentManager.delDepartment(line['id'])
                if params['parentID'] is None:
                    ret.Err = '从表格中找不到对应上层机构'
                return errorPage(msg="导入部门出错，表格第%d行:" % (i + 1) + str(ret.Err), url=request.url, parent=False)
        return successPage(msg="导入部门成功", url="/department/table", parent=False)

    return errorPage(title="不接受的请求类型")
