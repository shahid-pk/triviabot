#!usr/env/bin python

import os
import json


if __name__ == '__main__':
    questions = './questions.json'
    path = './jsonfiles'

    with open(questions, 'r', encoding = 'UTF-8') as f:
        mainjson = json.loads(f.read())

    for file in path:
        with open(os.path.join(path, file), 'r', encoding = 'UTF-8') as f:
            jsonls = json.loads(f.read())
        mainjson.extend(jsonls)

    with open(questions, 'w', encoding = 'UTF-8') as f:
        f.write(json.dumps(mainjson))
