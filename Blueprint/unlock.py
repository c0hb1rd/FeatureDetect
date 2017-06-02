import json

from flask import Blueprint, request, jsonify
from flask import render_template

from Core.AuthorityManager import KeyManager, RoleManager, ControlManager
from Core.DepartmentManager import DepartmentManager
from Core.PersonManager import PersonManager
from Helper.TimeHelper import TimeHelper
from Helper.UnlockHelp import matchFeatures, cache, decodeFeature
from Helper.UserHelper import formatSex
from config import (
    GAP
)

unlock = Blueprint("unlock", __name__, template_folder="templates")


def ctrlFormat(obj):
    obj.pop("detail", True)
    obj.pop("name", True)
    system = obj['system']
    obj.pop("system", True)
    return obj


@unlock.route("/userauth", methods=GAP)
def test():
    if request.method == 'POST':
        jsonData = request.get_json()
        # jsonData = request.data()
        # jsonData = json.loads(jsonData)
        # print(jsonData)
        name = request.args.get("name")
        keys = list(jsonData.keys())
        if 'authType' in keys and 'authData' in keys and 'scenario' in keys:
            # print(jsonData['authData'])
            # print(jsonData['authData']['fp'], type(jsonData['authData']['fp']))
            # print(jsonData['authData']['fp'].replace("\n", "").replace("/", "_").replace("+", "-"))
            print(jsonData['authType'])
            ret = matchFeatures(cache.Result, jsonData['authData'], jsonData['authType'])
            #     print(ret)
        else:
            return json.dumps({'status': 1, 'error': '提交数据格式不正确'})

        result = {'authResult': 0}
        if ret:
            print("Matched", ret['userName'])
            roles = PersonManager.getUserRoles(ret['id'])
            op = 0
            for role in roles:
                if '操作系统' in role['name']:
                    op = 1
            print(op)
            if op != 1:
                return jsonify({'status': 1, 'error': '无效用户'})
            ret = PersonManager.getUser(ret['id']).Result[0]
            # roles = PersonManager.getUserRoles(254)
            # ret = PersonManager.getUser(254).Result[0]
            ctrls = []
            for role in roles:
                keys = RoleManager().getKeysByRoleID(role['id']).Result
                for k in keys:
                    ctrlIDs = KeyManager().getCtrlByKeyID(k['keyID'])
                    for cID in ctrlIDs.Result:
                        ctrls.append(ControlManager().get(cID['controlID']).Result[0])
            sysMap = []
            dataMap = {}
            r = []
            data = {}
            for ctrl in ctrls:
                if ctrl['system'] not in sysMap:
                    sysMap.append(ctrl['system'])
                    dataMap[ctrl['menuID']] = ctrl['menuID']
                    system = ctrl['system']
                    data[system] = [ctrlFormat(ctrl)['id']]
                else:
                    system = ctrl['system']
                    data[system].append(ctrlFormat(ctrl)['id'])

            d = []
            for name in sysMap:
                ids = data[name]
                for cID in ids:
                    rt = ControlManager().getSortBySystem({'system': name, 'id': cID}).Result
                    if not rt:
                        continue
                    rt = rt[0]
                    rt['menuPercode'] = rt['flag']
                    rt['menuName'] = rt['name']
                    rt['menuId'] = rt['menuID']
                    rt['parentId'] = rt['parentID']
                    rt['menuState'] = rt['status']
                    rt['menuUrl'] = rt['detail']
                    rt.pop("flag", True)
                    rt.pop("parentID", True)
                    rt.pop("system", True)
                    rt.pop("status", True)
                    rt.pop("name", True)
                    rt.pop("detail", True)
                    rt.pop("menuID", True)
                    rt.pop("id", True)
                    d.append(rt)

            dep = DepartmentManager.getDepartment(ret['departmentID']).Result
            result = {
                'authResult': 1,
                'userInfo': {
                    'userName': ret['userName'],
                    'loginName': ret['loginName'],
                    'gender': formatSex(ret['gender']),
                    'department': dep[0]['name'] if len(dep) > 0 else "",
                    'recordTime': TimeHelper.formatTime(ret['recordTime']),
                    # 'roles': roles,
                    'userID': ret['userID'],
                    'password': "123456",
                    'username': ret['userName'],
                    'menus': d
                },
                'rights': 0
            }
        return json.dumps(result)
    elif request.method == 'GET':
        userID = request.args.get("usernum")
        system = request.args.get("name")
        r = PersonManager.getUserByUserID(userID)
        if r.Suc and r.Rows > 0:
            ret = r.Result[0]
            roles = PersonManager.getUserRoles(ret['id'])
            ret = PersonManager.getUser(ret['id']).Result[0]
            # roles = PersonManager.getUserRoles(254)
            # ret = PersonManager.getUser(254).Result[0]
            ctrls = []
            for role in roles:
                keys = RoleManager().getKeysByRoleID(role['id']).Result
                for k in keys:
                    ctrlIDs = KeyManager().getCtrlByKeyID(k['keyID'])
                    for cID in ctrlIDs.Result:
                        ctrls.append(ControlManager().get(cID['controlID']).Result[0])
            sysMap = []
            dataMap = {}
            r = []
            data = {}
            for ctrl in ctrls:
                if ctrl['system'] not in sysMap:
                    sysMap.append(ctrl['system'])
                    dataMap[ctrl['menuID']] = ctrl['menuID']
                    system = ctrl['system']
                    data[system] = [ctrlFormat(ctrl)['id']]
                else:
                    system = ctrl['system']
                    data[system].append(ctrlFormat(ctrl)['id'])

            d = []

            if system in data.keys():
                ids = data[system]
                for cID in ids:
                    rt = ControlManager().getSortBySystem({'system': system, 'id': cID}).Result
                    if not rt:
                        continue
                    rt = rt[0]
                    rt['menuPercode'] = rt['flag']
                    rt['menuName'] = rt['name']
                    rt['menuId'] = rt['menuID']
                    rt['parentId'] = rt['parentID']
                    rt['menuState'] = rt['status']
                    rt['menuUrl'] = rt['detail']
                    rt.pop("flag", True)
                    rt.pop("parentID", True)
                    rt.pop("system", True)
                    rt.pop("status", True)
                    rt.pop("name", True)
                    rt.pop("detail", True)
                    rt.pop("menuID", True)
                    rt.pop("id", True)
                    d.append(rt)

            dep = DepartmentManager.getDepartment(ret['departmentID']).Result
            result = {
                'authResult': 1,
                'userInfo': {
                    'userName': ret['userName'],
                    'loginName': ret['loginName'],
                    'gender': formatSex(ret['gender']),
                    'department': dep[0]['name'] if len(dep) > 0 else "",
                    'recordTime': TimeHelper.formatTime(ret['recordTime']),
                    # 'roles': roles,
                    'userID': ret['userID'],
                    'password': "123456",
                    'username': ret['userName'],
                    'menus': d
                },
                'rights': 0
            }
            # print(result)
            return json.dumps(result)
        else:
            return jsonify({})
    else:
        return json.dumps({'status': 1, 'error': '提交数据格式不正确'})
