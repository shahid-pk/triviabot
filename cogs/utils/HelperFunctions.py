import json
import discord
import os
import shutil


qmsg = """Options:
    1) {0}
    2) {1}
    3) {2}
    4) {3}"""


class User:
    def __init__(self, usrid, serverid):
        self.answered_correctly = 0
        self.answered_incorrectly = 0
        self.id = usrid
        self.mention = '<@{}>'.format(usrid)
        self.usersfile = os.path.join('./botstuff/servers/', serverid, 'Users.json')
        if not os.path.isfile(self.usersfile):
            with open(self.usersfile, 'w', encoding = "UTF-8") as f:
                f.write("{\n}")

    def write(self):
        with open(self.usersfile, 'r', encoding = 'UTF-8') as f:
            try:
                dictionary = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                dictionary = {}
        dictionary[self.id] = [self.answered_correctly, self.answered_incorrectly, self.mention]
        with open(self.usersfile, 'w', encoding = "UTF-8") as f:
            f.write(json.dumps(dictionary, indent = 4))

    def read(self):
        with open(self.usersfile, 'r', encoding = 'UTF-8') as f:
            try:
                dictionary = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                dictionary = {}
        try:
            self.answered_correctly = dictionary[self.id][0]
            self.answered_incorrectly = dictionary[self.id][1]
            self.mention = dictionary[self.id][2]
        except KeyError:
            pass

    def add_correct(self):
        self.answered_correctly += 1
        self.write()

    def add_incorrect(self):
        self.answered_incorrectly += 1
        self.write()


class Server:
    def __init__(self, servid):
        self.id = servid
        self.questionlist = []
        self.q = None
        self.already_answered = []
        self.totalquestions = 0
        self.do_trivia = False
        self.accept = True
        self.path = os.path.join('./botstuff/servers/', servid)
        os.makedirs(self.path, exist_ok = True)
        self.usersfile = os.path.join(self.path, 'Users.json')
        self.questions = os.path.join(self.path, 'questions.json')
        self.userdict = {}
        if not os.path.isfile(self.usersfile):
            with open(self.usersfile, 'w', encoding = "UTF-8") as f:
                f.write("{\n}")

        if not os.path.isfile(self.usersfile):
            with open(self.usersfile, 'w', encoding = "UTF-8") as f:
                f.write("{\n}")
        else:
            with open(self.usersfile, 'r', encoding = 'UTF-8') as f:
                try:
                    di = json.loads(f.read())
                except json.decoder.JSONDecodeError:
                    di = None
            if di:
                for usrid in di.keys():
                    user = User(usrid, self.id)
                    user.read()
                    self.userdict[usrid] = user

        if not os.path.isfile(self.questions):
            shutil.copy2('./botstuff/questions.json', self.questions)
        with open(self.questions, 'r', encoding = 'UTF-8') as file:
            self.questionlist = json.loads(file.read())
        with open('./botstuff/questions.json', 'r', encoding = 'UTF-8') as f:
            totalls = json.loads(f.read())
        self.totalquestions = len(totalls)

    def resetquestions(self):
        self.do_trivia = False
        os.remove(self.questions)
        shutil.copy2('./botstuff/questions.json', self.questions)
        with open(self.questions, 'r', encoding = 'UTF-8') as file:
            self.questionlist = json.loads(file.read())
        self.totalquestions = len(self.questionlist)

        self.resetscores()

    def resetscores(self):
        try:
            with open(self.usersfile, 'w', encoding = "UTF-8") as f:
                f.write("{\n}")
        except FileNotFoundError:
            pass
        self.userdict = {}

    def nextquestion(self):
        self.questionlist.pop(self.questionlist.index(self.q))
        if not self.questionlist:
            self.do_trivia = False
        self.q = None
        with open(self.questions, 'w', encoding = 'UTF-8') as file:
            file.write(json.dumps(self.questionlist, indent = 4))
        self.already_answered = []

        if self.questionlist:
            return False
        else:
            return True


def getserver(serverdict, ctx):
    try:
        server = serverdict[ctx.message.server.id]
    except KeyError:
        server = Server(ctx.message.server.id)
        serverdict[ctx.message.server.id] = server

    return server


def getuser(serverdict, ctx, mentions = False):
    if mentions:
        member = ctx.message.mentions[0]
    else:
        member = ctx.message.author
    try:
        user = serverdict[ctx.message.server.id].userdict[member.id]
    except KeyError:
        user = User(member.id, ctx.message.server.id)
        serverdict[ctx.message.server.id].userdict[member.id] = user

    return user


def getscoreboard(server, ctx):
    userls = ""
    numls = ""
    sepls = ''
    sortls = sorted(server.userdict.values(), key = lambda user: user.answered_correctly, reverse = True)
    for usr in sortls:
        member = discord.utils.get(ctx.message.server.members, mention = usr.mention)
        userls += member.name + '\n'
        numls += str(usr.answered_correctly) + '\n'
        sepls += ':\n'
    embed = discord.Embed(title = "Scoreboard", color = discord.Color.blue())
    if not userls:
        userls = '-'
    if not numls:
        numls = '-'
    if not sepls:
        sepls = ':'
    embed.add_field(name = 'Users', value = userls)
    embed.add_field(name = ':', value = sepls)
    embed.add_field(name = 'Scores', value = numls)

    return embed


def dispense(server: Server, ctx):
    print("Dispensing question to {}...".format(ctx.message.server))
    if not server.questionlist:
        print("-" * 12)
        print("Ran out of questions in {}. Resetting question list...".format(ctx.message.server))
        print("-" * 12)
        server.resetquestions()
    server.q = server.questionlist[0]

    return server
