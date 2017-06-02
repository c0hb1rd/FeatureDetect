import requests
import json
import json
import base64
from base64 import urlsafe_b64encode as urlEncode

def decodeFeature(obj):
    return base64.urlsafe_b64decode(obj.replace("\n", "").replace("/", "_").replace("+", "-"))

def loadTemp(filename):
    with open(filename, "rb+") as f: tmp = f.read()
    return str(urlEncode(tmp))

url = 'http://127.0.0.1:8086/userauth'

headers = {
    "Content-Type": "Application/json"
}

f =  open("iris2.template", "r")

data = {
    'authType': 4,
    'authData': {
        # 'fp': loadTemp("fp.template"),
        # 'fv': loadTemp("fv.template"),
        # 'face': "this is face",
        'iris': f.read()
    },
    'scenario': 0
}

data = json.dumps(data)


ret = requests.post(url, headers=headers, data=data)
for k,v in json.loads(ret.text).items():
    print(k, ':', v)
