from flask import Flask
from jinja2 import filters

from Blueprint.authority import authority
from Blueprint.department import department
from Blueprint.record import record
from Blueprint.unlock import unlock
from Blueprint.users import users
from Helper.AuthorityHelper import formatKind
from Helper.DepartmentHelpler import departmentName, departmentNameToTable
from Helper.OtherHelper import errorPage
from Helper.TimeHelper import TimeHelper
from Helper.UserHelper import formatRoles, formatRights, listUser, formatSex
from config import (
    SER_PORT,
    SER_HOST
)

app = Flask(__name__)
app.config.from_object("config")

app.register_blueprint(users)
app.register_blueprint(department)
app.register_blueprint(record)
app.register_blueprint(unlock)
app.register_blueprint(authority)


filters.FILTERS['formatTime'] = TimeHelper.formatTime
filters.FILTERS['formatSex'] = formatSex
filters.FILTERS['departmentName'] = departmentName
filters.FILTERS['departmentNameToTable'] = departmentNameToTable
filters.FILTERS['listUser'] = listUser
filters.FILTERS['formatRights'] = formatRights
filters.FILTERS['formatRoles'] = formatRoles
filters.FILTERS['formatKind'] = formatKind


@app.errorhandler(404)
def pageNotFound(e):
    return errorPage(title="页面未找到", msg="页面未找到")


@app.errorhandler(400)
def webError(e):
    return errorPage(title="异常", msg="服务端异常")

if __name__ == '__main__':
    app.run(host=SER_HOST, port=SER_PORT, threaded=True)
