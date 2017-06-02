import base64

from flask import Blueprint, request, jsonify
from flask import render_template

from Core.PersonManager import PersonManager, Person
from Helper.TimeHelper import TimeHelper
from Helper.UnlockHelp import addMemory, decodeFeature
from Helper.UserHelper import getImagePath
from config import (
    GAP
)

record = Blueprint("record", __name__, template_folder="templates")


@record.route("/record", methods=GAP)
def recordPerson():
    if request.method == 'POST':
        info = {'status': 0}
        data = request.json
        for k in data.keys():
            print(k)
        if data:
            try:
                userInfo = data['userInfo']
                bioInfo = data['bioInfo']

                person = Person()

                person.recordTime = TimeHelper.getStamp()

                person.userName = userInfo['userName']
                person.userLogo = userInfo.get("userLogo", None)
                person.userID = userInfo['userID']
                person.gender = userInfo['gender']

                person.fp = bioInfo['fpTpl']
                person.fv = bioInfo['fvTpl']
                person.face = bioInfo['faceTpl']
                person.iris = bioInfo['irisTpl']

                person.fpImg = bioInfo['fpImg']
                person.fvImg = bioInfo['fvImg']
                person.faceImg = bioInfo['faceImg']
                person.irisImg = bioInfo['irisImg']
                if person.userLogo:
                    person.hasLogo = 1
                else:
                    person.hasLogo = 0
                personDict = person.__dict__
            except KeyError as e:
                print(str(e))
                return jsonify({'Key Error': 'Key ' + str(e) + ' not found'})

            r = PersonManager.addUser(personDict)

            if not r.Suc:
                info = {
                    'status': 1,
                    'error': "该身份证已注册" if "1062" in str(r.Err) else str(r.Err)
                }
            else:
                personDict['id'] = r.Result['LAST_INSERT_ID()']
                addMemory(personDict)
                if person.hasLogo:
                    imageData = decodeFeature(person.userLogo)
                    imagePath = getImagePath(personDict['id'])
                    with open(imagePath + ".png", "wb+") as f: f.write(imageData)
                    with open(imagePath + "_face.png", "wb+") as f: f.write(decodeFeature(bioInfo['faceImg']))
                    with open(imagePath + "_fp.png", "wb+") as f: f.write(decodeFeature(bioInfo['fpImg']))
                    with open(imagePath + "_fv.png", "wb+") as f: f.write(decodeFeature(bioInfo['fvImg']))
                    with open(imagePath + "_iris.png", "wb+") as f: f.write(decodeFeature(bioInfo['irisImg']))

        return jsonify(info)
    else:
        return render_template("status/status.html", title="页面未找到", message="页面未找到", url="/", flag=False)
