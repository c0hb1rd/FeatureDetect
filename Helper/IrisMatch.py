import base64
import ctypes
import os
import time


currentPath = os.getcwd() + '\Helper\\'


# def decodeFeature(obj):
#     return base64.urlsafe_b64decode(obj.replace("\n", "").replace("/", "_").replace("+", "-"))
    # return base64.urlsafe_b64decode(obj)


class IrisMatcher:
    def __init__(self):
        self.result = None
        self.dll = ctypes.WinDLL(currentPath + "whsusbapi.dll")
        # self.dll = ctypes.WinDLL("whsusbapi.dll")
        self.initRet = self.dll.HS_Initialize()
        self.record = None
        self.result = None

        def matchCallback(a1, a2, a3, a4):
            self.result = a4

        MCB = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
        self.callBack = MCB(matchCallback)
        self.dll.HS_SetMatchCallback(self.callBack)
        self.dll.HS_GetDeviceList()

    def createRecord(self):
        self.record = self.dll.HS_CreateMatchRecord()

    def insertTemp(self, feature, fID):
        return self.dll.HS_InsertTemplateB(self.record, feature, len(feature), fID)

    def setTemp(self, feature):
        return self.dll.HS_SetTemplateA(self.record, feature, len(feature))

    def releaseRecord(self):
        return self.dll.HS_ReleaseMatchRecord(self.record)

    def startMatch(self):
        ret = self.dll.HS_StartMatch(0, self.record)
        tmp = None
        print(ret)
        if ret == 0:
            start = time.time()
            while self.result is None:
                continue
            tmp = self.result
            self.result = None
        self.releaseRecord()
        return tmp

    def finalize(self):
        self.dll.HS_Finalize()

    def getMatchResult(self, featureA, featureB):
        self.createRecord()
        self.setTemp(featureA)
        self.insertTemp(featureB, "ID")
        return self.startMatch()


# from Core.PersonManager import PersonManager
#
# user = PersonManager.getUser(256).Result[0]
# feat = decodeFeature(user['iris'])
# irisMatcher = IrisMatcher()
#
# for i in range(100):
#     print(i, irisMatcher.getMatchResult(feat, feat))
#
#
# irisMatcher.finalize()
