from flask import render_template


def successPage(title="操作成功", msg="成功", url="/", parent=True):
    return render_template("status/status.html", title=title, message=msg, url=url, flag=True, parent=parent)


def errorPage(title="操作出错", msg="出错", url="/", parent=True):
    return render_template("status/status.html", title=title, message=msg, url=url, flag=False, parent=parent)

