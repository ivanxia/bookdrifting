import os
import json

def create_user():
    with open("user.dat") as f:
        lines = f.readlines()


    for line in lines:
        items = line.split(' ')
        body = {
            'id': int(items[0]),
            'name': items[1],
            'password': items[2],
            'description': items[3].strip()
        }

        cmd = "curl -X POST localhost:7777/v1/user -d '%s'" % json.dumps(body)

        os.system(cmd)

create_user()
