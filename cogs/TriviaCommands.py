import re

from discord.ext import commands
from cogs.utils.Permissions import permissionChecker
from botstuff.dataclasses import *


class TriviaCommands:
    def __init__(self, bot):
        self.bot = bot
        self.serverdict = {}

        os.makedirs("servers", exist_ok = True)

        for i in os.listdir("./servers"):
            server = Server(i)
            server.init_server()
            self.serverdict[i] = server

    @commands.command(pass_context = True)
    async def trivia(self, ctx):
        """
        Get a trivia question.
        """
        server = self.getserver(ctx)

        print("Dispensing question to {}...".format(ctx.message.server))
        if not server.questionlist:
            print("-" * 12)
            print("Ran out of questions in {}. Resetting questionlist...".format(ctx.message.server))
            print("-" * 12)
            server.init_server()
        server.q = server.questionlist[0]
        await self.bot.say(server.q.question + "\n" + qmsg.format(server.q.options[0], server.q.options[1],
                                                                  server.q.options[2], server.q.options[3]))
        print('Question "{}" dispensed to {}.'.format(server.q.question, ctx.message.server))

    @commands.command(pass_context = True)
    @permissionChecker(check = 'is_owner')
    async def bypass(self, ctx):
        """
        Bypass a question.
        """
        server = self.getserver(ctx)
        if server.q:
            print("{} in {} is trying to bypass a question.".format(ctx.message.author, ctx.message.server))
            self.bypassquestion(server)
            await self.bot.say("Question thrown off stack.")
        else:
            print("{0} in {1} is trying to bypass a question which hasn't been asked. {0} pls"
                  .format(ctx.message.author, ctx.message.server))
            await self.bot.say("There is no question to bypass.")

    @staticmethod
    def bypassquestion(server):
        server.questionlist.pop(server.questionlist.index(server.q))
        os.remove(os.path.join("./servers", server.id, 'pickled', str(server.q.qno) + '.q'))
        del server.q
        server.q = None
        server.already_answered = []

    @commands.command(pass_context = True)
    async def a(self, ctx, *, answer: str = None):
        """
        Answer the question.
        """
        server = self.getserver(ctx)

        if ctx.message.author.id not in server.already_answered:
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
                    await self.bot.say("Congratulations, {}! You got it!".format(ctx.message.author.mention))
                    self.bypassquestion(server)
                else:
                    print("{} answered incorrectly.".format(str(ctx.message.author)))
                    await self.bot.say("Wrong answer, {}.".format(ctx.message.author.mention))

            elif server.q and not answer:
                print(".. this question: {}".format(server.q.question))
                print(".. with an empty answer! {} pls".format(ctx.message.author))
            else:
                print(".. a non-existent question! {} pls".format(ctx.message.author))
                await self.bot.say("No question was asked. Get a question first with `^trivia`.")

    @commands.command(pass_context = True, hidden = True)
    @permissionChecker(check = "is_owner")
    async def reset(self, ctx):
        server = self.getserver(ctx)
        print("Resetting questions in {}...".format(ctx.message.server))
        server.resetquestions()
        server.init_server()
        print("Questions reset.")
        print("-" * 12)
        await self.bot.say("Questions reset.")

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
            server.init_server()

        return server

    @commands.command(pass_context = True)
    async def suggest(self, ctx):
        """
        Suggest a question.
        Requests to supply info timeout after 20 seconds.
        Be sure to include the letter s with the command prefix after it, such as:
        s^ *your stuff here*
        """

        def check1(msg):
            if re.search("(s\^)\s(.*?)(\?)", msg.content):
                return True
            else:
                return False

        def check2(msg):
            if re.search("(s\^)\s(.*?)", msg.content):
                return True
            else:
                return False

        def check3(msg):
            if re.search("(s\^)\s([1-4]+?)", msg.content):
                try:
                    int(re.search("(s\^)\s([1-4]+?)", msg.content).group(2))
                    return True
                except ValueError:
                    return False
            else:
                return False

        timeout = 20
        print("{} in {} is trying to suggest a question.".format(ctx.message.author, ctx.message.server))
        await self.bot.say("Write the question:")
        ques = await self.bot.wait_for_message(timeout, author = ctx.message.author, channel = ctx.message.channel,
                                         check = check1)
        ques = re.search("(s\^)\s(.*\?)", ques.content).group(2)
        print("{} suggests: {}".format(ctx.message.author, ques))
        if ques:
            opls = []
            for i in range(1, 5):
                await self.bot.say("Write option {}:".format(str(i)))
                op = await self.bot.wait_for_message(timeout, author = ctx.message.author, channel = ctx.message.channel,
                                               check = check2)
                if not op:
                    return
                op = re.search("(s\^)\s(.*)", op.content).group(2)
                print("    option {}: {}".format(i, op))
                opls.append(op)
            await self.bot.say("Which is the right answer? (Enter a number pl0x)")
            answno = await self.bot.wait_for_message(timeout, author = ctx.message.author, channel = ctx.message.channel,
                                               check = check3)
            if not answno:
                return
            answno = int(re.search("(s\^)\s([1-4])", answno.content).group(2))
            answ = opls[answno - 1]
            print("    The correct answer is no. {}: {}".format(answno, answ))
            os.makedirs("./suggested", exist_ok = True)
            fileno = len(os.listdir("./suggested"))
            with open(os.path.join("./suggested", "q{}.json".format(fileno)), 'w', encoding = "UTF-8") as file:
                file.write(jsontemplate.format(ques, opls[0], opls[1], opls[2], opls[3], answ, answno))
            await self.bot.say("Your suggestion has been submitted. Dank.")


def setup(bot):
    x = TriviaCommands(bot)
    bot.add_cog(x)
