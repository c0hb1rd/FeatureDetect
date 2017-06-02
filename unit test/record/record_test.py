import requests
import json
from base64 import urlsafe_b64encode as urlEncode
import random


def loadTemp(filename):
    with open(filename, "rb+") as f: tmp = f.read()
    return urlEncode(tmp).decode()

url = 'http://127.0.0.1:8086/record'

headers = {'Content-Type': 'application/json'}
defaultID = 44050199901001001
count = 0


dataTmp = {
    'userInfo': {
        'loginName': 't3st',
        'gender': 1,
    },
    'bioInfo': {
        'fp': loadTemp("fp.template"),
        'fv': loadTemp("fv.template"),
        'face': '''aGVsbG8=''',
        'iris': loadTemp("iris.template")
    }
}

fristNames = "赵、钱、孙、李、周、吴、郑、王、冯、陈、楮、卫、蒋、沈、韩、杨、朱、秦、尤、许、何、吕、施、张、孔、曹、严、华".split("、")
with open("name.txt", "r") as  f: lastNames = f.read().strip().split("、")
departments = ['706所1部', '706所2部', '706所3部', '706所4部', '203所1部', '203所2部', '203所3部', '203所4部']
# positions = ['安全研发', '渗透测试', '运行维护', '项目测试', '程序开发', '漏洞挖掘', '市场调研', "产品经理"]
# positions = ["1组", "2组", "3组", "4组", "5组", "6组", "7组", "8组", "9组"]

for i in range(0, 63):
    randomFirst = random.randint(0, len(fristNames) - 1)
    name = fristNames[randomFirst] + lastNames[i]
    data = dataTmp
    data['userInfo']['userLogo'] = loadTemp("user%d.jpg" % i)
    data['userInfo']['userName'] = name
    # data['userInfo']['department'] = departments[random.randint(0, len(departments) - 1)]
    # data['userInfo']['position'] = positions[random.randint(0, len(positions) - 1)]
    # data['userInfo']['department'] = "departments[random.randint(0, len(departments) - 1)]"
    # data['userInfo']['position'] = "positions[random.randint(0, len(positions) - 1)]"
    data['userInfo']['userID'] = defaultID
    rep = requests.post(url, data=json.dumps(data), headers=headers)
    print(json.loads(rep.text))
    defaultID += 1
    count += 1
