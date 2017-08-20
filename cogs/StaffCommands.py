import asyncio
import os
from discord.ext import commands
from cogs.utils.HelperFunctions import getserver, Server, qmsg, getuser
from cogs.utils.Permissions import permissionChecker


# criteria for determining who can access the staff commands
perm = 'ban_members'


class StaffCommands:

    def __init__(self, bot):
        self.bot = bot
        self.serverdict = {}

        os.makedirs("./botstuff/servers", exist_ok = True)

        # load the servers from the folder, where each folder is named with the server id.
        # a new Server object is created using the id, and it is stored in `serverdict` with the same id as key.
        for i in os.listdir("./botstuff/servers"):
            self.serverdict[i] = Server(i)

    @commands.command(pass_context = True, aliases = ['start'])
    @permissionChecker(check = perm)
    async def starttrivia(self, ctx):
        """
        Calls ,trivia, until the bot runs out of questions.
        """
        # get the server
        server = getserver(self.serverdict, ctx)

        # if it isn't already continuously dispensing questions, continue. else, don't do anything
        # this is because, if this command was called multiple times, the bot would have multiple async instances inside
        # the while loop.
        if not server.do_trivia:

            # as explained above, allows for only one instance.
            server.do_trivia = True

            # if a question was asked prior to starting the command, retell the question
            if server.q:
                retellq = True
            else:
                retellq = False

            # this loop stops when `do_trivia` is set to False by another command, `stoptrivia`.
            while server.do_trivia:

                # if questionlist is empty, the look should stop.
                if not server.questionlist:
                    server.do_trivia = False
                    break

                # if a question was asked but was answered, thereby clearing the property `q`, post a question.
                if not server.q:

                    # basically sets `q` to a new question
                    server.dispense(ctx)

                    # nicely format the question
                    await self.bot.say(
                        server.q['question'] + "\n" + qmsg.format(server.q['options'][0],
                                                                  server.q['options'][1],
                                                                  server.q['options'][2],
                                                                  server.q['options'][3]))

                    print('"{}" dispensed.'.format(server.q['question']))

                # if the previous retell check passed, go into this block, set retell to False as to not post the
                # question every 2 seconds(it has happened, btw), and send the question. nothing peculiar about it.
                elif retellq:
                    retellq = False
                    await self.bot.say(
                        server.q['question'] + "\n" + qmsg.format(server.q['options'][0],
                                                                  server.q['options'][1],
                                                                  server.q['options'][2],
                                                                  server.q['options'][3]))
                    print('Retold question "{}" in {}.'.format(server.q['question'], ctx.message.server))

                # async sleep for 2 seconds.
                await asyncio.sleep(2)

    @commands.command(pass_context = True, aliases = ['stop'])
    @permissionChecker(check = perm)
    async def stoptrivia(self, ctx):
        """
        Stop the command ,starttrivia.
        """
        # see above command to know how `do_trivia` fits in
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

        # set the server.q property to the question at the top of the question list, and send it.
        server.dispense(ctx)
        await self.bot.say(
            server.q['question'] + "\n" + qmsg.format(server.q['options'][0], server.q['options'][1],
                                                      server.q['options'][2], server.q['options'][3]))
        print('"{}" dispensed.'.format(server.q['question']))

    @commands.command(pass_context = True)
    @permissionChecker(check = perm)
    async def resetscore(self, ctx):
        """
        Resets a user's score.
        You may reset someone else's score by mentioning them.
        """
        server = getserver(self.serverdict, ctx)

        # if more than one mention was included in the message, the first mention is our target. otherwise, the author.
        if len(ctx.message.mentions) > 0:
            user = getuser(self.serverdict, ctx, mentions = ctx.message.mentions[0])
        else:
            user = getuser(self.serverdict, ctx)

        # sets the user's points to 0, and writes it to the Users.json file for the server.
        user.points = 0
        user.write()

        # removes the user from server.userdict
        server.userdict.pop(user.id)

        await self.bot.say("{}'s score has been reset.".format(user.mention))

    @commands.command(pass_context = True)
    @permissionChecker(check = perm)
    async def count(self, ctx):
        """
        Get number of questions.
        """
        server = getserver(self.serverdict, ctx)

        # simple math. totalquestions is the total, answered is the difference between the total and the remaining,
        # and the remaining is questionlist.
        await self.bot.say("I have a total of {} questions, {} of which has been answered, and {} remain unanswered."
                           .format(server.totalquestions, server.totalquestions - len(server.questionlist),
                                   len(server.questionlist)))

    @commands.command(pass_context = True)
    @permissionChecker(check = perm)
    async def resetallscores(self, ctx):
        """
        Resets all the user's scores.
        You shouldn't need to do this in most cases, but it's there. Just in case.
        """
        server = getserver(self.serverdict, ctx)

        # does exactly what it says on the tin - resets the scores.
        server.resetscores()
        await self.bot.say("All scores reset.")

    @commands.command(pass_context = True)
    @permissionChecker(check = perm)
    async def reset(self, ctx):
        """
        Resets/starts over the questions.
        Basically resets the questions stack.
        """
        server = getserver(self.serverdict, ctx)
        print("Resetting questions in {}...".format(ctx.message.server), end = ' ')

        # does exactly what it says on the tin - resets the questions.
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
        """
        server = getserver(self.serverdict, ctx)

        # if there is a question to bypass
        if server.q:
            q = server.q

            # bypasses the question and returns whether said question was the last one or not.
            b = server.nextquestion()
            print("{} in {} is trying to bypass a question...".format(ctx.message.author, ctx.message.server))
            await self.bot.say('Question "{}" thrown off stack.'.format(q['question']))
            print('Bypassed "{}".'.format(q['question']))

            # if it is, display the scoreboard and reset the questions.
            if b:
                print("Out of questions. displaying scoreboard...", end = ' ')
                await self.bot.say("That's all I have, folks!")
                embed = server.getscoreboard()
                await self.bot.say(embed = embed)
                server.resetquestions()
                print("Scoreboard displayed")
        else:
            print("which hasn't been asked! {0} pls".format(ctx.message.author))
            await self.bot.say("There is no question to bypass.")


def setup(bot):
    cog = StaffCommands(bot)
    bot.add_cog(cog)
