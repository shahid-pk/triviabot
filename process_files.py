#!usr/env/bin python

import os
import shutil


def getjsontxt(thing):
    with open(thing, 'r', encoding = 'UTF-8') as f:
        return f.read()


if __name__ == '__main__':
    jsonls = []
    for file in os.listdir('./jsonfiles'):
        jsontxt = getjsontxt(file)
        for i in jsonls:
            if jsontxt == i:
                os.remove(os.path.join('./jsonfiles', file))
        jsonls.append(jsontxt)
        os.rename(os.path.join('./jsonfiles', file), os.path.join('./jsonfiles', 'q' + file))
        shutil.copy2(os.path.join('./jsonfiles', 'q' + file), './question_src')


    x = 0
    for i in os.listdir('./question_src'):
        y = str(x)
        while len(y) < 4:
            y = "0" + y
        os.rename(os.path.join('./question_src', i), os.path.join('./question_src', "q{}.json".format(y)))
        x += 1
