import discord
from cogs.utils.Permissions import permissionChecker
from discord.ext import commands
import json
import os
import asyncio
import shutil

qmsg = """Options:
    1) {0}
    2) {1}
    3) {2}
    4) {3}"""


class User:
    def __init__(self, usrid, server):
        self.answered_correctly = 0
        self.answered_incorrectly = 0
        self.id = usrid
        self.mention = '<@{}>'.format(usrid)
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
        self.usersfile = os.path.join(self.path, 'Users.json')
        self.questions = os.path.join(self.path, 'questions.json')
        self.userdict = {}

        os.makedirs(os.path.join("./botstuff/servers", self.id, 'session'), exist_ok = True)

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
                        self.userdict[usrid] = user

        if not os.path.isfile(self.questions):
            shutil.copy2('./botstuff/questions.json', self.questions)
            with open(self.questions, 'r', encoding = 'UTF-8') as file:
                self.questionlist = json.loads(file.read())
            self.totalquestions = len(self.questionlist)

    def resetquestions(self):
        shutil.rmtree(os.path.dirname(self.questions))
        os.makedirs(os.path.dirname(self.questions), exist_ok = True)

        shutil.copy2('./botstuff/questions.json', self.questions)
        with open(self.questions, 'r', encoding = 'UTF-8') as file:
            self.questionlist = json.loads(file.read())
        self.totalquestions = len(self.questionlist)

        self.resetscores()

    def resetscores(self):
        try:
            os.remove(self.usersfile)
        except FileNotFoundError:
            pass
        self.userdict = {}

    def nextquestion(self):
        self.questionlist.pop(self.questionlist.index(self.q))
        with open(self.questions, 'w', encoding = 'UTF-8') as file:
            file.write(json.dumps(self.questionlist))
        self.already_answered = []

        if self.questionlist:
            return False
        else:
            return True


class TriviaCommands:
    def __init__(self, bot):
        self.bot = bot
        self.serverdict = {}

        os.makedirs("./botstuff/servers", exist_ok = True)

        for i in os.listdir("./botstuff/servers"):
            self.serverdict[i] = Server(i)

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
    def dispense(server: Server, ctx):
        print("Dispensing question to {}...".format(ctx.message.server))
        if not server.questionlist:
            print("-" * 12)
            print("Ran out of questions in {}. Resetting question list...".format(ctx.message.server))
            print("-" * 12)
            server.resetquestions()
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
            b = server.nextquestion()
            await self.bot.say('Question "{}" thrown off stack.'.format(server.q.question))
            if b:
                print("Out of questions. displaying scoreboard...")
                await self.bot.say("That's all I have, folks!")
                embed = self.getscoreboard(server, ctx)
                await self.bot.say(embed = embed)
                server.resetquestions()
                print("Scoreboard displayed")
        else:
            print("{0} in {1} is trying to bypass a question which hasn't been asked. {0} pls"
                  .format(ctx.message.author, ctx.message.server))
            await self.bot.say("There is no question to bypass.")

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
                    user.add_correct()
                    await self.bot.say("Congratulations, {}! You got it!".format(ctx.message.author.mention))
                    done = server.nextquestion()
                    if done:
                        print("Out of questions. displaying scoreboard...")
                        await self.bot.say("That's all I have, folks!")
                        embed = self.getscoreboard(server, ctx)
                        await self.bot.say(embed = embed)
                        server.resetquestions()
                        print("Scoreboard displayed")
                else:
                    user.add_incorrect()
                    print("{} answered incorrectly.".format(str(ctx.message.author)))
                    await self.bot.say("Wrong answer, {}.".format(ctx.message.author.mention))

            elif server.q and not answer:
                print(".. this question: {}".format(server.q.question))
                print(".. with an empty answer! {} pls".format(ctx.message.author))
            else:
                print(".. a non-existent question! {} pls".format(ctx.message.author))
                await self.bot.say("No question was asked. Get a question first with `^trivia`.")

        server.accept = True

    @commands.command(pass_context = True, hidden = True)
    @permissionChecker(check = "is_owner")
    async def reset(self, ctx):
        server = self.getserver(ctx)
        print("Resetting questions in {}...".format(ctx.message.server))
        server.resetquestions()
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
            server = Server(ctx.message.server.id)
            self.serverdict[ctx.message.server.id] = server

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


def setup(bot):
    x = TriviaCommands(bot)
    bot.add_cog(x)
