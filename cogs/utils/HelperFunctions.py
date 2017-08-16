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
    """
    represents a User
    """
    def __init__(self, usrid, serverid, mention):
        self.points = 0
        self.id = usrid
        self.mention = mention
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
        dictionary[self.id] = [self.points, self.mention]
        with open(self.usersfile, 'w', encoding = "UTF-8") as f:
            f.write(json.dumps(dictionary, indent = 4))

    def read(self):
        with open(self.usersfile, 'r', encoding = 'UTF-8') as f:
            try:
                dictionary = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                dictionary = {}
        try:
            self.points = dictionary[self.id][0]
            self.mention = dictionary[self.id][1]
        except KeyError:
            pass

    def add_correct(self):
        self.points += 10
        self.write()

    def add_incorrect(self):
        self.points -= 5
        self.write()


class Server:
    """
    represents a server.
    """
    def __init__(self, servid):
        # the server id
        self.id = servid

        # the list of questions, the list of users who have already answered the current question,
        # and the dictionary of all users in said server who have participated in trivia.
        self.questionlist = []
        self.already_answered = []
        self.userdict = {}

        # the total number of questions, and the variable `q` to hold the dictionary of the currently asked question.
        self.totalquestions = 0
        self.q = None

        # a boolean to check whether or not to continually ask questions,
        # and another to check if a correct answer is currently being processed.
        self.do_trivia = False
        self.accept = True

        # make the server folder if it's not already created.
        path = os.path.join('./botstuff/servers/', servid)
        os.makedirs(path, exist_ok = True)

        # define the users.json and the questions.json files, which hold a dictionary of user ids and points,
        # and a list of questions, respectively.
        self.usersfile = os.path.join(path, 'Users.json')
        self.questions = os.path.join(path, 'questions.json')

        # fix up Users.json.
        # ----------------
        # if it's not created yet, create it.
        if not os.path.isfile(self.usersfile):
            with open(self.usersfile, 'w', encoding = "UTF-8") as f:
                f.write("{\n}")

        # if it is, try to load the dictionary of users.
        else:
            with open(self.usersfile, 'r', encoding = 'UTF-8') as f:
                try:
                    di = json.loads(f.read())
                except json.decoder.JSONDecodeError:
                    di = None
            # if decoding the dictionary works, convert into `User` objects and load them into `self.userdict`
            if di:
                for usrid, vls in di.items():
                    user = User(usrid, self.id, vls[1])
                    user.read()
                    self.userdict[usrid] = user

        # fix up questions.json
        # ----------------
        # if it's not created, copy the questions from botstuff.
        if not os.path.isfile(self.questions):
            shutil.copy2('./botstuff/questions.json', self.questions)

        # open the file, decode it, and keep it around as `self.questionlist`
        with open(self.questions, 'r', encoding = 'UTF-8') as file:
            self.questionlist = json.loads(file.read())

        # open the original questions.json, and count the total number of questions in there.
        # this is to ensure the `,count` command is accurate in the event where a question is answered,
        # and therefore is removed from the server's questions.json. 
        # which necessitates getting the correct total number of questions from the original questions.json file.
        with open('./botstuff/questions.json', 'r', encoding = 'UTF-8') as f:
            totalls = json.loads(f.read())
        self.totalquestions = len(totalls)

    def resetquestions(self):
        """
        resets the question stack for the server, and resets all the scores.
        """
        # stop asking questions, if the bot was doing that.
        self.do_trivia = False

        # remove the questions.json file and copy a fresh set of questions from the original questions.json file
        os.remove(self.questions)
        shutil.copy2('./botstuff/questions.json', self.questions)

        # load the questions.json file and keep it as `self.questionlist`
        with open(self.questions, 'r', encoding = 'UTF-8') as file:
            self.questionlist = json.loads(file.read())

        # figure out the total number of questions
        self.totalquestions = len(self.questionlist)

        # reset the current asked question
        self.q = None

        # resets the list of users who already answered
        self.already_answered = []

        # does exactly what it says on the tin - resets the scores.
        self.resetscores()

    def resetscores(self):
        """
        resets the scores in the server
        """
        # open the user file and write an empty dictionary to it
        with open(self.usersfile, 'w', encoding = "UTF-8") as f:
            f.write("{\n}")

        # set the `self.userdict` to an empty dictionary, since scores are reset
        self.userdict = {}

    def nextquestion(self) -> bool:
        """
        moves into the next question
        """
        # remove the current question from the question list
        self.questionlist.pop(self.questionlist.index(self.q))

        # reset the list of users who already answered
        self.already_answered = []

        # if the question list has run out of questions, stop continually asking questions.
        if not self.questionlist:
            self.do_trivia = False

        # reset the current question to None.
        self.q = None

        # update the server's `questions.json` with the new `self.questionlist` after removing a question.
        with open(self.questions, 'w', encoding = 'UTF-8') as file:
            file.write(json.dumps(self.questionlist, indent = 4))

        # if there are more questions left in the list, return False.
        # otherwise, return True
        # this is used to know when a server runs out of questions, and so, display the final scoreboard
        if self.questionlist:
            return False
        else:
            return True

    def dispense(self, ctx):
        """
        get a question from questionlist

        :param ctx:
        :return:
        """
        # if questionlist is empty, and a question is required: reset the question stack.
        if not self.questionlist:
            print("-" * 12)
            print("Ran out of questions in {}. Resetting question list...".format(ctx.message.server))
            print("-" * 12)
            self.resetquestions()
        print("Dispensing question to {}...".format(ctx.message.server))
        # set the current question to the first item in questionlist
        self.q = self.questionlist[0]

    def getscoreboard(self, ctx) -> discord.Embed:
        """
        constructs a scoreboard from the server's Users.json file

        :param ctx: the context
        :return: an Embed object
        """
        # a string of usernames separated by linebreaks
        userls = ""

        # a string of user scores, separated by linebreaks
        numls = ""

        # a string of separators between the two columns of usernames and scores.
        sepls = ''

        # construct a list out of the values of `userdict`, which are User objects, sorted descending by points.
        sortls = sorted(self.userdict.values(), key = lambda user: user.points, reverse = True)

        # construct the columns which are going to be used in the fields
        for usr in sortls:
            # get the discord.Member object from the server member list using the member's mention
            member = discord.utils.get(ctx.message.server.members, mention = usr.mention)
            userls += member.name + '\n'
            numls += str(usr.points) + '\n'
            sepls += 'َ\n'

        # make a new embed
        embed = discord.Embed(title = "Scoreboard", color = discord.Color.blue())

        # default values, in case someone requests a scoreboard when it's empty
        if not userls:
            userls = '-'
        if not numls:
            numls = '-'
        if not sepls:
            sepls = 'َ'

        # add fields
        embed.add_field(name = 'Users', value = userls)
        embed.add_field(name = 'َ', value = sepls)
        embed.add_field(name = 'Scores', value = numls)

        return embed


def getserver(serverdict, ctx) -> Server:
    """
    get the server the context belongs to, either from `serverdict` or by making a new Server object and inserting it
    into `serverdict`.

    :param serverdict: a dictionary: keys are server ids, values are Server objects
    :param ctx: the context which started the command
    """
    try:
        server = serverdict[ctx.message.server.id]
    except KeyError:
        server = Server(ctx.message.server.id)
        serverdict[ctx.message.server.id] = server

    return server


def getuser(serverdict, ctx, mentions = False) -> User:
    """
    get the user who sent the message, either from `serverdict` or by making a new User object and inserting it
    into the `self.userdict` property of the server whence the command was called.

    :param serverdict: a dictionary: keys are server ids, values are Server objects
    :type serverdict: dict
    :param ctx: the context which started the command
    :param mentions: defaults to False, and otherwise is a mentioned discord.User object, using ctx.message.mentions[0]
    :return: a User object
    :type:
    """
    # if what's needed is a mentioned user, return mentioned user. else, return who called the command.
    if mentions:
        member = mentions
    else:
        member = ctx.message.author

    # get the user either from `.userdict` or make a new User object.
    try:
        user = serverdict[ctx.message.server.id].userdict[member.id]
    except KeyError:
        user = User(member.id, ctx.message.server.id, member.mention)
        serverdict[ctx.message.server.id].userdict[member.id] = user

    return user
