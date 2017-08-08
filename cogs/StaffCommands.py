import asyncio
import os
from discord.ext import commands
from cogs.utils.HelperFunctions import getserver, Server, dispense, qmsg, getscoreboard, getuser
from cogs.utils.Permissions import permissionChecker

perm = 'ban_members'


class StaffCommands:

    def __init__(self, bot):
        self.bot = bot
        self.serverdict = {}

        os.makedirs("./botstuff/servers", exist_ok = True)

        for i in os.listdir("./botstuff/servers"):
            self.serverdict[i] = Server(i)

    @commands.command(pass_context = True, aliases = ['start'])
    @permissionChecker(check = perm)
    async def starttrivia(self, ctx):
        """
        Calls ,trivia, until the bot runs out of questions.
        """
        server = getserver(self.serverdict, ctx)
        if not server.do_trivia:
            server.do_trivia = True
            if server.q:
                retellq = True
            else:
                retellq = False
            while server.do_trivia:
                if not server.questionlist:
                    break
                if not server.q:
                    server = dispense(server, ctx)
                    await self.bot.say(
                        server.q['question'] + "\n" + qmsg.format(server.q['options']['op1'],
                                                                  server.q['options']['op2'],
                                                                  server.q['options']['op3'],
                                                                  server.q['options']['op4']))
                    print('Question "{}" dispensed to {}.'.format(server.q['question'], ctx.message.server))
                elif retellq:
                    retellq = False
                    await self.bot.say(
                        server.q['question'] + "\n" + qmsg.format(server.q['options']['op1'],
                                                                  server.q['options']['op2'],
                                                                  server.q['options']['op3'],
                                                                  server.q['options']['op4']))
                    print('Retold question "{}" in {}.'.format(server.q['question'], ctx.message.server))
                await asyncio.sleep(2)

    @commands.command(pass_context = True, aliases = ['stop'])
    @permissionChecker(check = perm)
    async def stoptrivia(self, ctx):
        """
        Stop the command ,starttrivia.
        """
        server = getserver(self.serverdict, ctx)
        server.do_trivia = False
        await self.bot.say("Trivia stopped.")

    @commands.command(pass_context = True, aliases = ['question'])
    @permissionChecker(check = perm)
    async def trivia(self, ctx):
        """
        Get a single trivia question.
        """
        server = getserver(self.serverdict, ctx)
        server = dispense(server, ctx)
        await self.bot.say(
            server.q['question'] + "\n" + qmsg.format(server.q['options']['op1'], server.q['options']['op2'],
                                                      server.q['options']['op3'], server.q['options']['op4']))
        print('Question "{}" dispensed to {}.'.format(server.q['question'], ctx.message.server))

    @commands.command(pass_context = True)
    @permissionChecker(check = perm)
    async def resetscore(self, ctx):
        """
        Resets the caller's score.
        """
        user = getuser(self.serverdict, ctx)
        self.serverdict[ctx.message.server.id].userdict.pop(user.id)
        await self.bot.say("{}'s score has been reset.".format(user.mention))

    @commands.command(pass_context = True)
    @permissionChecker(check = perm)
    async def count(self, ctx):
        """
        Get number of questions.
        """
        server = getserver(self.serverdict, ctx)
        await self.bot.say("I have a total of {} questions, {} of which has been answered, and {} remain unanswered."
                           .format(server.totalquestions, server.totalquestions - len(server.questionlist),
                                   len(server.questionlist)))

    @commands.command(pass_context = True)
    @permissionChecker(check = perm)
    async def resetallscores(self, ctx):
        """
        Resets all the user's scores.
        You shouldn't need to do this anyways.
        """
        server = getserver(self.serverdict, ctx)
        server.resetscores()
        await self.bot.say("All scores reset.")

    @commands.command(pass_context = True)
    @permissionChecker(check = perm)
    async def reset(self, ctx):
        """
        Resets/starts over the questions.
        """
        server = getserver(self.serverdict, ctx)
        print("Resetting questions in {}...".format(ctx.message.server))
        server.resetquestions()
        print("Questions reset.")
        print("-" * 12)
        await self.bot.say("Questions reset.")

    @commands.command(pass_context = True)
    @permissionChecker(check = perm)
    async def bypass(self, ctx):
        """
        Bypass a question.
        This most likely will never have to be used.
        Only in the very unlikely scenario where there are less than 3 users in the server
        and all of them answered wrongly, will it get any use.
        """
        server = getserver(self.serverdict, ctx)
        if server.q:
            print("{} in {} is trying to bypass a question.".format(ctx.message.author, ctx.message.server))
            await self.bot.say('Question "{}" thrown off stack.'.format(server.q['question']))
            b = server.nextquestion()
            if b:
                print("Out of questions. displaying scoreboard...")
                await self.bot.say("That's all I have, folks!")
                embed = getscoreboard(server, ctx)
                await self.bot.say(embed = embed)
                server.resetquestions()
                print("Scoreboard displayed")
        else:
            print("{0} in {1} is trying to bypass a question which hasn't been asked. {0} pls"
                  .format(ctx.message.author, ctx.message.server))
            await self.bot.say("There is no question to bypass.")


def setup(bot):
    cog = StaffCommands(bot)
    bot.add_cog(cog)
