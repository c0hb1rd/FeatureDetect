import base64
import os

import io
from hxns_bio_sdk.finger import FeatureJudge as FingerFeatureJudge
from hxns_bio_sdk.basic_face import FaceFinder, FeatureJudge as FaceFeatureJudge, ModuleTerminate

from Core.PersonManager import PersonManager
from Helper.IrisMatch import IrisMatcher

cache = PersonManager.getUserList()


faceJudgeScore = 0.5  # 脸部分数阈值
minPrintJudgeScore = 0.5  # 指纹分数阈值
minVeinJudgeScore = 0.5  # 指静脉分数阈值
irisMatcher = None


def addMemory(person):
    cache.Result.append(person)
    cache.Rows += 1


def getMemory():
    return cache


def refreshMemory():
    global cache
    cache = PersonManager.getUserList()


def judgeFaceFeature(featureA, featureB):
    return FaceFeatureJudge().Judge(featureA, featureB)


def getFaceFeature(imageBuf, param):
    faceFinder = FaceFinder()

    faceFinder.SetParamMaxFace(param)
    r = faceFinder.FindFace(imageBuf)

    if r['error_code'] !=0:
        info = {'error': "Find Face Error"}
    else:
        r = faceFinder.GetFaceFeatures()
        if r['error_code'] != 0:
            info = {'error': "Get Face Feature Error"}
        else:
            if len(r['features']) > 1:
                info = {'error': "Too Many Faces"}
            else:
                print("Find Features")
                return True, r['features'][0].binary_feature.buf
    return False, info


def batchJudgeFaceFeature(featureA):
    userIDs = []
    for user in cache.Result:
        r = judgeFaceFeature(featureA, user['face'])
        if r['error_code'] != 0:
            pass
        else:
            score = round(r['score'], 3)
            if score - faceJudgeScore > 0:
                userIDs.append(user['f_id'])
    return userIDs


def judgeFingerFeature(kind, featureA, featureB):
    judge = FingerFeatureJudge()
    if kind == 'vein':
        r = judge.JudgeFingerVein(decodeFeature(featureA), decodeFeature(featureB))
    elif kind == 'print':
        r = judge.JudgeFingerPrint(decodeFeature(featureA), decodeFeature(featureB))
    else:
        r = {"error_code": 1}

    if r['error_code'] != 0:
        maxScore = 0
    else:
        maxScore = round(r['score'], 3)
        maxScore = r['score']

    return maxScore


def getMatchUsers(printFeature, veinFeature, userIDs):
    matchUserList = []
    for uID in userIDs:
        user = PersonManager.getUser(uID)
        printFeatureList = [
            base64.b64decode(user['f_fingerprint_feature_1']),
            base64.b64decode(user['f_fingerprint_feature_2']),
            base64.b64decode(user['f_fingerprint_feature_3']),
        ]
        veinFeatureList = [
            base64.b64decode(user['f_fingervein_feature_1']),
            base64.b64decode(user['f_fingervein_feature_2']),
            base64.b64decode(user['f_fingervein_feature_3']),
        ]

        printScore = judgeFingerFeature("print", base64.b64decode(printFeature), printFeatureList)
        veinScore = judgeFingerFeature("vein", base64.b64decode(veinFeature), veinFeatureList)

        if printScore > minPrintJudgeScore and veinScore > minVeinJudgeScore:
            matchUser = {"printScore": printScore, "veinScore": veinScore, "user": user}
            matchUserList.append(matchUser)
    return matchUserList


def getBestMatchUser(matchUserList):
    matcherUser = None
    maxScore = 0.0
    for user in matchUserList:
        score = user['printScore'] + user['veinPrintScore']
        if score > maxScore:
            maxScore = score
            matcherUser = user['user']
    return matcherUser


def isNone(obj):
    return True if obj is None else False


def decodeFeature(obj):
    return base64.urlsafe_b64decode(obj.replace("\n", "").replace("/", "_").replace("+", "-"))
    # return base64.urlsafe_b64decode(obj)


def matchFeatures(users, features, authType):
    global irisMatcher
    if not irisMatcher:
        irisMatcher = IrisMatcher()
    r = []
    count = 0
    for user in users:
        count += 1
        print(count, 'count')
        if authType in [3, 5]:
            uID = user['id']
            imagePath = os.path.join(os.getcwd(), "static", "Image", "Users", "%s_face.png" % str(uID))
            with open(imagePath, "rb+") as f: buf = f.read()
            ret1, feat1 = getFaceFeature(buf, 20)
            ret2, feat2 = getFaceFeature(decodeFeature(features['face']), 20)
            if ret1 and ret2:
                try:
                    ret = judgeFaceFeature(feat1, feat2)
                except:
                    continue
                if ret['error_code'] == 0:
                    if ret['score'] > 0.5:
                        return user
                    else:
                        continue
                else:
                    continue
            else:
                continue
        if authType in [4, 5]:
            ret = irisMatcher.getMatchResult(decodeFeature(user['iris']), decodeFeature(features['iris']))
            if ret == 1:
                return user
            else:
                continue
        if authType in [1, 5]:
            if not judgeFingerFeature('print', user['fp'], features['fp']) > 0.5:
                continue
        if authType in [2, 5]:
            if not judgeFingerFeature('vein', user['fv'], features['fv']) > 0.5:
                continue
        return user

    return r


# s = io.BytesIO()
# with open(os.path.join(os.getcwd(), "static", "Image", "Users" , "259_face.png"), "rb+") as f:
#     buf = f.read()


# ret, feat = getFaceFeature(buf, 20)
# print(len(feat))
# if ret:
#     ret = judgeFaceFeature(feat, feat)
#     print(ret)
#
# print(2)
# ret = M(tempA, tempA)
# print(ret)
