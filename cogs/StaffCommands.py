import asyncio
import os
from discord.ext import commands
from cogs.utils.TriviaBackend import getserver, Server, qmsg, getuser
from cogs.utils.Permissions import permissionChecker


# criteria for determining who can access the staff commands
perm = 'ban_members'


class StaffCommands:

    def __init__(self, bot):
        self.bot: commands.Bot = bot
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

    @commands.command(pass_context = True)
    @permissionChecker(check = perm)
    async def tn(self, ctx, mode: str = None):
        """
        Toggle trivia night mode on or off.
        :param mode: whether to toggle it on or off
        """
        server = getserver(self.serverdict, ctx)

        if not mode:
            await self.bot.say(f'TriviaNight mode is currently {server.tn}.')
            return

        elif mode.lower() in ['true', 'on']:
            server.settnmode()

        elif mode.lower() in ['false', 'off']:
            server.unsettnmode()

        await self.bot.say(f'TriviaNight mode is set to {server.tn}.')

    @commands.command(pass_context = True)
    @permissionChecker(check = 'is_owner')
    async def endtrivianight(self, ctx):
        """
        Moves all the trivia night questions into the normal questions file.
        """
        server = getserver(self.serverdict, ctx)

        if not server.tn:
            await self.bot.say("I can't end TriviaNight when it hasn't started yet!")
            return

        await self.bot.say('TriviaNight has ended.')
        embed = server.getscoreboard()
        await self.bot.say(embed = embed)
        server.endtrivianight()

    @commands.command(pass_context = True)
    @permissionChecker(check = perm)
    async def conf(self, ctx, key: str = None, value: str = None):
        """
        Configure server-specific variables.
        Configurable variables are fuzzymin, which is the minimum number of characters to use fuzzy matching,
        and fuzzythreshold, which is the match percentage to accept a match as legit
        :param ctx:
        :param key: The thing you want to configure
        :param value: The thing you want the key to be set to.
        :return:
        """
        server = getserver(self.serverdict, ctx)

        # if no key is given, ignore
        if not key:
            print('conf is called with no variables. ignored.')
            return

        # if key isn't one of the configurables, say so and ignore
        if key not in ['fuzzymin', 'fuzzythreshold']:
            await self.bot.say('Only `fuzzymin`(minimum number of characters to use fuzzy matching) and '
                               '`fuzzythreshold`(match percentage for fuzzy matching) are accepted as keys.')
            return

        # if a value is not given, display the current value
        if not value:
            print(f'conf is called with no value. displaying value of {key}...')
            k = getattr(server, key)
            await self.bot.say(f'The value of {key} is {k}')
            return

        # turn value into an integer and make sure it's between 1 and 100
        try:
            v = int(value)
        except ValueError:
            await self.bot.say('Only numerical values between `1` and `100` are allowed.')
            return

        if not 1 <= v <= 100:
            await self.bot.say('Only numerical values between `1` and `100` are allowed.')
            return

        # set the attribute
        setattr(server, key, v)
        await self.bot.say(f'{key} set to {v}.')


def setup(bot):
    cog = StaffCommands(bot)
    bot.add_cog(cog)
