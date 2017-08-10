from discord.ext import commands
from cogs.utils.HelperFunctions import getserver, getuser, getscoreboard


class TriviaCommands:

    def __init__(self, bot):
        self.bot = bot
        self.serverdict = self.bot.cogs['StaffCommands'].serverdict

    @commands.command(pass_context = True)
    async def a(self, ctx, *, answer: str = None):
        """
        Answer the question.
        """
        server = getserver(self.serverdict, ctx)
        user = getuser(self.serverdict, ctx)

        if answer is not None and ctx.message.author.id not in server.already_answered:
            print("{} in {} is trying to answer...".format(ctx.message.author, ctx.message.server))
            server.already_answered.append(ctx.message.author.id)
            if server.q and answer:
                print(".. this question: {}".format(server.q['question']))
                try:
                    numanswer = int(answer)
                except ValueError:
                    numanswer = 0
                if server.accept and \
                        (answer.lower() == server.q['answer'].lower() or numanswer == int(server.q['answerno'])):
                    server.accept = False
                    print("{} answered correctly.".format(str(ctx.message.author)))
                    print("-" * 12)
                    user.add_correct()
                    await self.bot.say("Congratulations, {}! You got it!".format(ctx.message.author.mention))
                    done = server.nextquestion()
                    if done:
                        print("Out of questions. displaying scoreboard...")
                        await self.bot.say("That's all I have, folks!")
                        embed = getscoreboard(server, ctx)
                        await self.bot.say(embed = embed)
                        server.resetquestions()
                        print("Scoreboard displayed")
                    server.accept = True
                elif answer.lower() == server.q['answer'].lower() or numanswer == int(server.q['answerno']):
                    print("{} answered correctly, but was too slow!".format(ctx.message.author))
                    await self.bot.say("Too slow, {}!".format(ctx.message.author.mention))
                else:
                    user.add_incorrect()
                    print("{} answered incorrectly.".format(str(ctx.message.author)))
                    await self.bot.say("Wrong answer, {}.".format(ctx.message.author.mention))

            elif server.q and not answer:
                print(".. this question: {}".format(server.q['question']))
                print(".. with an empty answer! {} pls".format(ctx.message.author))
            else:
                print(".. a non-existent question! {} pls".format(ctx.message.author))
                await self.bot.say("No question was asked. Get a question first with `^trivia`.")
        elif ctx.message.author.id in server.already_answered:
            await self.bot.say("You've already used up your answer, {}.".format(ctx.message.author.mention))

    @commands.command(pass_context = True, aliases = ['leaderboard', 'board'])
    async def scoreboard(self, ctx):
        """
        Show everyone's score.
        """
        server = getserver(self.serverdict, ctx)
        print("{} in {} is trying to get the scoreboard.".format(ctx.message.author, ctx.message.server))
        embed = getscoreboard(server, ctx)
        await self.bot.say(embed = embed)
        print("Scoreboard displayed.")

    @commands.command(pass_context = True, aliases = ['points'])
    async def score(self, ctx):
        """
        Get number of times a user answered correctly.
        You may check someone else's score by mentioning them, such as: ,score *mention*
        """
        try:
            m = ctx.message.mentions[0]
        except IndexError:
            m = False
        if m:
            user = getuser(self.serverdict, ctx, mentions = True)
        else:
            user = getuser(self.serverdict, ctx)
        await self.bot.say("{} has answered {} questions correctly, and {} incorrectly."
                           .format(user.mention, user.answered_correctly, user.answered_incorrectly))


def setup(bot):
    x = TriviaCommands(bot)
    bot.add_cog(x)
