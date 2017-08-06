import os
import shutil
import pickle
import json


jsontemplate = ('{{\n'
                '  "question": "{0}",\n'
                '  "options": {{\n'
                '    "op1": "{1}",\n'
                '    "op2": "{2}",\n'
                '    "op3": "{3}",\n'
                '    "op4": "{4}"\n'
                '  }},\n'
                '  "answer": "{5}",\n'
                '  "answerno": "{6}"\n'
                '}}')

qmsg = """Options:
    1) {0}
    2) {1}
    3) {2}
    4) {3}"""


def load_json(path):
    quels = []
    qno = 0
    for json_q in os.listdir(os.path.join(path, "question_src")):
        qno += 1
        with open(os.path.join(path, "question_src", json_q), 'r', encoding = "UTF-8") as f:
            rawjson = f.read()
        que = json.loads(rawjson)
        questiontext = que['question']
        optiondict = que['options']
        o1 = optiondict['op1']
        o2 = optiondict['op2']
        o3 = optiondict['op3']
        o4 = optiondict['op4']
        answertext = que['answer']
        answerno = que['answerno']
        question = Question(questiontext, answertext, answerno, o1, o2, o3, o4, qno)
        with open(os.path.join(path, 'pickled', str(question.qno) + '.q'), 'wb') as picklefile:
            pickle.dump(question, picklefile)
        quels.append(question)

    return quels


class Question:
    def __init__(self, question, answer, answerno, op1, op2, op3, op4, qno):
        self.question = question
        self.answer = answer
        self.answerno = int(answerno)
        self.options = [op1, op2, op3, op4]
        self.qno = qno


class Server:
    def __init__(self, servid):
        self.wasinit = False
        self.id = servid
        self.questionlist = []
        self.q = None
        self.already_answered = []
        self.totalquestions = 0

<<<<<<< HEAD
        os.makedirs(os.path.join("servers", self.id, 'pickled'), exist_ok = True)

    def init_server(self):
        questionls = []
        for i in os.listdir(os.path.join("./servers", self.id, 'pickled')):
            with open(os.path.join("./servers", self.id, 'pickled', i), 'rb') as picklefile:
=======
        os.makedirs(os.path.join("./botstuff/servers", self.id, 'pickled'), exist_ok = True)

    def init_server(self):
        questionls = []
        for i in os.listdir(os.path.join("./botstuff/servers", self.id, 'pickled')):
            with open(os.path.join("./botstuff/servers", self.id, 'pickled', i), 'rb') as picklefile:
>>>>>>> initial commit
                question = pickle.load(picklefile)
            questionls.append(question)
        else:
            try:
<<<<<<< HEAD
                shutil.copytree("./question_src", os.path.join("./servers", self.id, 'question_src'))
            except FileExistsError:
                shutil.rmtree(os.path.join("./servers", self.id, 'question_src'))
                shutil.copytree("./question_src", os.path.join("./servers", self.id, 'question_src'))
            questionls = load_json(os.path.join("./servers", self.id))
=======
                shutil.copytree("./botstuff/question_src", os.path.join("./botstuff/servers", self.id, 'question_src'))
            except FileExistsError:
                shutil.rmtree(os.path.join("./botstuff/servers", self.id, 'question_src'))
                shutil.copytree("./botstuff/question_src", os.path.join("./botstuff/servers", self.id, 'question_src'))
            questionls = load_json(os.path.join("./botstuff/servers", self.id))
>>>>>>> initial commit
        self.wasinit = True
        self.questionlist = questionls
        self.totalquestions = len(questionls)

    def resetquestions(self):
<<<<<<< HEAD
        shutil.rmtree(os.path.join("./servers", self.id, 'pickled'))
        os.makedirs(os.path.join("./servers", self.id, 'pickled'), exist_ok = True)
=======
        shutil.rmtree(os.path.join("./botstuff/servers", self.id, 'pickled'))
        os.makedirs(os.path.join("./botstuff/servers", self.id, 'pickled'), exist_ok = True)
>>>>>>> initial commit
