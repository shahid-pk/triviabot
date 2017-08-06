import discord
from cogs.utils.Permissions import permissionChecker
from discord.ext import commands
import json
import os
import asyncio
import pickle
import shutil


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


class User:
    def __init__(self, member, server):
        self.answered_correctly = 0
        self.answered_incorrectly = 0
        self.id = member.id
        self.member = member
        self.mention = member.mention
        self.usersfile = os.path.join('./botstuff/servers/', server, 'Users.json')
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
        jsontxt = json.dumps(dictionary, indent=4)
        with open(self.usersfile, 'w', encoding = "UTF-8") as f:
            f.write(jsontxt)

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


class Server:
    def __init__(self, servid, bot):
        self.wasinit = False
        self.id = servid
        self.questionlist = []
        self.q = None
        self.already_answered = []
        self.totalquestions = 0
        self.do_trivia = False
        self.accept = True

        os.makedirs(os.path.join("./botstuff/servers", self.id, 'pickled'), exist_ok = True)
        self.usersfile = os.path.join('./botstuff/servers/', servid, 'Users.json')

        if not os.path.isfile(self.usersfile):
            with open(self.usersfile, 'w', encoding = "UTF-8") as f:
                f.write("{\n}")
            self.userdict = {}
        else:
            with open(self.usersfile, 'r', encoding = 'UTF-8') as f:
                try:
                    di = json.loads(f.read())
                    self.userdict = {}
                    for k in di.keys():
                        member = discord.utils.get(bot.connection._servers[self.id].members, id = k)
                        user = User(member, self.id)
                        self.userdict[member.id] = user
                except json.decoder.JSONDecodeError:
                    self.userdict = {}

    def init_server(self):
        questionls = []
        for i in os.listdir(os.path.join("./botstuff/servers", self.id, 'pickled')):
            with open(os.path.join("./botstuff/servers", self.id, 'pickled', i), 'rb') as picklefile:
                question = pickle.load(picklefile)
            questionls.append(question)
        else:
            try:
                shutil.copytree("./botstuff/question_src", os.path.join("./botstuff/servers", self.id, 'question_src'))
            except FileExistsError:
                shutil.rmtree(os.path.join("./botstuff/servers", self.id, 'question_src'))
                shutil.copytree("./botstuff/question_src", os.path.join("./botstuff/servers", self.id, 'question_src'))
            questionls = load_json(os.path.join("./botstuff/servers", self.id))
        self.wasinit = True
        self.questionlist = questionls
        self.totalquestions = len(questionls)

    def resetquestions(self):
        shutil.rmtree(os.path.join("./botstuff/servers", self.id, 'pickled'))
        os.makedirs(os.path.join("./botstuff/servers", self.id, 'pickled'), exist_ok = True)

    def resetscores(self):
        try:
            os.remove(os.path.join('./botstuff/servers', self.id, 'Users.json'))
        except FileNotFoundError:
            pass
        self.userdict = {}


class TriviaCommands:
    def __init__(self, bot):
        self.bot = bot
        self.serverdict = {}

        os.makedirs("./botstuff/servers", exist_ok = True)

        for i in os.listdir("./botstuff/servers"):
            server = Server(i, self.bot)
            server.init_server()
            self.serverdict[i] = server

    @commands.command(pass_context = True)
    async def starttrivia(self, ctx):
        """
        Calls ^trivia, until the bot runs out of questions.
        """
        server = self.getserver(ctx)
        server.do_trivia = True
        while server.do_trivia:
            if not server.questionlist:
                server.do_trivia = False
                break
            if not server.q:
                server = self.dispense(server, ctx)
                await self.bot.say(server.q.question + "\n" + qmsg.format(server.q.options[0], server.q.options[1],
                                                                          server.q.options[2], server.q.options[3]))
                print('Question "{}" dispensed to {}.'.format(server.q.question, ctx.message.server))
            await asyncio.sleep(2)

    @commands.command(pass_context = True)
    async def stoptrivia(self, ctx):
        """
        Stop the command ^starttrivia.
        """
        server = self.getserver(ctx)
        server.do_trivia = False
        await self.bot.say("Trivia stopped.")

    @commands.command(pass_context = True)
    async def trivia(self, ctx):
        """
        Get a single trivia question.
        """
        server = self.getserver(ctx)
        server = self.dispense(server, ctx)
        await self.bot.say(server.q.question + "\n" + qmsg.format(server.q.options[0], server.q.options[1],
                                                                  server.q.options[2], server.q.options[3]))
        print('Question "{}" dispensed to {}.'.format(server.q.question, ctx.message.server))

    @staticmethod
    def dispense(server, ctx):
        print("Dispensing question to {}...".format(ctx.message.server))
        if not server.questionlist:
            print("-" * 12)
            print("Ran out of questions in {}. Resetting question list...".format(ctx.message.server))
            print("-" * 12)
            server.init_server()
            server.resetscores()
        server.q = server.questionlist[0]

        return server

    @commands.command(pass_context = True)
    @permissionChecker(check = 'is_owner')
    async def bypass(self, ctx):
        """
        Bypass a question.
        """
        server = self.getserver(ctx)
        if server.q:
            print("{} in {} is trying to bypass a question.".format(ctx.message.author, ctx.message.server))
            b = self.bypassquestion(server)
            await self.bot.say('Question "{}" thrown off stack.'.format(server.q.question))
            if b:
                print("Out of questions. displaying scoreboard...")
                await self.bot.say("That's all I have, folks!")
                embed = self.getscoreboard(server, ctx)
                await self.bot.say(embed = embed)
                server.resetscores()
                print("Scoreboard displayed")
        else:
            print("{0} in {1} is trying to bypass a question which hasn't been asked. {0} pls"
                  .format(ctx.message.author, ctx.message.server))
            await self.bot.say("There is no question to bypass.")

    @staticmethod
    def bypassquestion(server):
        server.questionlist.pop(server.questionlist.index(server.q))
        os.remove(os.path.join("./botstuff/servers", server.id, 'pickled', str(server.q.qno) + '.q'))
        del server.q
        server.q = None
        server.already_answered = []

        if server.questionlist:
            return False
        else:
            return True

    @commands.command(pass_context = True)
    async def a(self, ctx, *, answer: str = None):
        """
        Answer the question.
        """
        server = self.getserver(ctx)
        user = self.getuser(ctx)

        if server.accept and ctx.message.author.id not in server.already_answered:
            server.accept = False
            print("{} in {} is trying to answer...".format(ctx.message.author, ctx.message.server))
            server.already_answered.append(ctx.message.author.id)
            if server.q and answer:
                print(".. this question: {}".format(server.q.question))
                try:
                    numanswer = int(answer)
                except ValueError:
                    numanswer = 0
                if answer.lower() == server.q.answer.lower() or numanswer == server.q.answerno:
                    print("{} answered correctly.".format(str(ctx.message.author)))
                    print("-" * 12)
                    user.answered_correctly += 1
                    user.write()
                    server.accept = True
                    await self.bot.say("Congratulations, {}! You got it!".format(ctx.message.author.mention))
                    done = self.bypassquestion(server)
                    if done:
                        print("Out of questions. displaying scoreboard...")
                        await self.bot.say("That's all I have, folks!")
                        embed = self.getscoreboard(server, ctx)
                        await self.bot.say(embed = embed)
                        server.resetscores()
                        print("Scoreboard displayed")
                else:
                    user.answered_incorrectly += 1
                    server.accept = True
                    print("{} answered incorrectly.".format(str(ctx.message.author)))
                    await self.bot.say("Wrong answer, {}.".format(ctx.message.author.mention))

            elif server.q and not answer:
                print(".. this question: {}".format(server.q.question))
                print(".. with an empty answer! {} pls".format(ctx.message.author))
                server.accept = True
            else:
                print(".. a non-existent question! {} pls".format(ctx.message.author))
                server.accept = True
                await self.bot.say("No question was asked. Get a question first with `^trivia`.")

    @commands.command(pass_context = True, hidden = True)
    @permissionChecker(check = "is_owner")
    async def reset(self, ctx):
        server = self.getserver(ctx)
        print("Resetting questions in {}...".format(ctx.message.server))
        server.resetquestions()
        server.init_server()
        server.resetscores()
        print("Questions reset.")
        print("-" * 12)
        await self.bot.say("Questions reset.")

    @commands.command(pass_context = True)
    async def scoreboard(self, ctx):
        """
        Show everyone's score.
        """
        server = self.getserver(ctx)
        print("{} in {} is trying to get the scoreboard.".format(ctx.message.author, ctx.message.server))
        embed = self.getscoreboard(server, ctx)
        await self.bot.say(embed = embed)
        print("Scoreboard displayed.")

    @commands.command(pass_context = True)
    async def score(self, ctx):
        """
        Get number of times a user answered correctly.
        You may check someone else's score by mentioning them, such as: ^score *mention*
        """
        try:
            m = ctx.message.mentions[0]
        except IndexError:
            m = False
        if m:
            user = self.getuser(ctx, mentions = True)
        else:
            user = self.getuser(ctx)
        await self.bot.say("{} has answered {} questions correctly, and {} incorrectly."
                           .format(user.mention, user.answered_correctly, user.answered_incorrectly))

    @commands.command(pass_context = True)
    async def resetscore(self, ctx):
        """
        Resets the caller's score.
        """
        user = self.getuser(ctx)
        self.serverdict[ctx.message.server.id].userdict.pop(user.id)
        await self.bot.say("Reset {}'s score.".format(user.mention))

    @commands.command(pass_context = True)
    @permissionChecker(check = 'is_owner')
    async def resetallscores(self, ctx):
        """
        Resets all the user's scores.
        """
        server = self.getserver(ctx)
        server.resetscores()
        await self.bot.say("All scores reset.")

    @commands.command(pass_context = True)
    async def count(self, ctx):
        """
        Get number of questions.
        """

        server = self.getserver(ctx)

        await self.bot.say("I have a total of {} questions, {} of which has been answered, and {} remain unanswered."
                           .format(server.totalquestions, server.totalquestions - len(server.questionlist),
                                   len(server.questionlist)))

    def getserver(self, ctx):
        try:
            server = self.serverdict[ctx.message.server.id]
        except KeyError:
            server = Server(ctx.message.server.id, self.bot)
            self.serverdict[ctx.message.server.id] = server
            server.init_server()

        return server

    def getuser(self, ctx, mentions = False):
        if mentions:
            member = ctx.message.mentions[0]
        else:
            member = ctx.message.author
        try:
            user = self.serverdict[ctx.message.server.id].userdict[member.id]
        except KeyError:
            user = User(member, ctx.message.server.id)
            self.serverdict[ctx.message.server.id].userdict[member.id] = user
            user.read()

        return user

    @staticmethod
    def getscoreboard(server, ctx):
        userls = ""
        numls = ""
        sortls = sorted(server.userdict.values(), key = lambda user: user.answered_correctly, reverse = True)
        for usr in sortls:
            member = discord.utils.get(ctx.message.server.members, mention = usr.mention)
            name = member.display_name
            userls += name + '\n'
            numls += str(usr.answered_correctly) + '\n'
        embed = discord.Embed(title = "Scoreboard", color = discord.Color.blue())
        if not userls:
            userls = " "
        if not numls:
            numls = " "
        embed.add_field(name = 'Users:', value = userls)
        embed.add_field(name = " ", value = " ")
        embed.add_field(name = 'Scores:', value = numls)

        return embed

    # @commands.command(pass_context = True)
    # async def suggest(self, ctx, *args):
    #     """
    #     Suggest a question.
    #     Requests to supply info timeout after 20 seconds.
    #     Be sure to include the letter s with the command prefix after it, such as:
    #     s^ *your stuff here*
    #     Alternatively, you may suggest an question in one message, using this format:
    #     ^suggest *question* *option1* *option2* *option3* *option4* *answer(as a number)*
    #     if a parameter consists of more than one word, you'll have to put it inside quotes.
    #     """
    #     print("{} in {} is trying to suggest a question.".format(ctx.message.author, ctx.message.server))
    #     if args:
    #         if len(args) == 6:
    #             que = args[0]
    #             op1 = args[1]
    #             op2 = args[2]
    #             op3 = args[3]
    #             op4 = args[4]
    #             answno = args[5]
    #             answ = args[int(answno)]
    #
    #             os.makedirs("./botstuff/suggested", exist_ok = True)
    #             fileno = len(os.listdir("./botstuff/suggested"))
    #             with open(os.path.join("./botstuff/suggested", "q{}.json".format(fileno)), 'w',
    #                       encoding = "UTF-8") as file:
    #                 file.write(jsontemplate.format(que, op1, op2, op3, op4, answ, answno))
    #             print("{} in {} suggested: {}\n"
    #                   "    option 1: {}\n"
    #                   "    option 2: {}\n"
    #                   "    option 3: {}\n"
    #                   "    option 4: {}\n"
    #                   "    The correct answer is no.{}: {}".format(ctx.message.author, ctx.message.server, que, op1,
    #                                                                op2, op3, op4, answno, answ))
    #             print("-" * 12)
    #             await self.bot.say("Your suggestion has been submitted. Dank.")
    #         else:
    #             print("Unrecognized format")
    #             print("-" * 12)
    #             await self.bot.say("Incorrect format. Type ^help suggest for help using this command.")
    #     else:
    #         def check1(msg):
    #             if re.search("(s\^)\s(.*?)(\?)", msg.content):
    #                 return True
    #             else:
    #                 return False
    #
    #         def check2(msg):
    #             if re.search("(s\^)\s(.*?)", msg.content):
    #                 return True
    #             else:
    #                 return False
    #
    #         def check3(msg):
    #             if re.search("(s\^)\s([1-4]+?)", msg.content):
    #                 try:
    #                     int(re.search("(s\^)\s([1-4]+?)", msg.content).group(2))
    #                     return True
    #                 except ValueError:
    #                     return False
    #             else:
    #                 return False
    #
    #         timeout = 20
    #         await self.bot.say("Write the question:")
    #         ques = await self.bot.wait_for_message(timeout, author = ctx.message.author,
    #                                                channel = ctx.message.channel, check = check1)
    #         ques = re.search("(s\^)\s(.*\?)", ques.content).group(2)
    #         print("{} suggests: {}".format(ctx.message.author, ques))
    #         if ques:
    #             opls = []
    #             for i in range(1, 5):
    #                 await self.bot.say("Write option {}:".format(str(i)))
    #                 op = await self.bot.wait_for_message(timeout, author = ctx.message.author,
    #                                                      channel = ctx.message.channel,
    #                                                      check = check2)
    #                 if not op:
    #                     return
    #                 op = re.search("(s\^)\s(.*)", op.content).group(2)
    #                 print("    option {}: {}".format(i, op))
    #                 opls.append(op)
    #             await self.bot.say("Which is the right answer? (Enter a number pl0x)")
    #             answno = await self.bot.wait_for_message(timeout, author = ctx.message.author,
    #                                                      channel = ctx.message.channel,
    #                                                      check = check3)
    #             if not answno:
    #                 return
    #             answno = int(re.search("(s\^)\s([1-4])", answno.content).group(2))
    #             answ = opls[answno - 1]
    #             print("    The correct answer is no. {}: {}".format(answno, answ))
    #             os.makedirs("./botstuff/suggested", exist_ok = True)
    #             fileno = len(os.listdir("./botstuff/suggested"))
    #             with open(os.path.join("./botstuff/suggested", "q{}.json".format(fileno)), 'w',
    #                       encoding = "UTF-8") as file:
    #                 file.write(jsontemplate.format(ques, opls[0], opls[1], opls[2], opls[3], answ, answno))
    #             await self.bot.say("Your suggestion has been submitted. Dank.")


def setup(bot):
    x = TriviaCommands(bot)
    bot.add_cog(x)
