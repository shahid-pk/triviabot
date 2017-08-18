import asynciofrom discord.ext import commandsfrom cogs.utils.HelperFunctions import getserver, getuserclass TriviaCommands:    # timeout before deleting messages in seconds    timeout = 2    def __init__(self, bot):        self.bot: commands.Bot = bot        # get the same serverdict as loaded by the StaffCommands cog.        self.serverdict = self.bot.cogs['StaffCommands'].serverdict    @commands.command(pass_context = True)    async def a(self, ctx, *, answer: str = None):        """        Answer the question.        """        server = getserver(self.serverdict, ctx)        user = getuser(self.serverdict, ctx)        # return if no question was asked        if not server.q:            bm = await self.bot.say(f':question: | {ctx.message.author.mention} No question asked.')            await asyncio.sleep(self.timeout)            await self.bot.delete_message(bm)            await self.bot.delete_message(ctx.message)            return        # return if no answer was provided, or it wasn't one of the options        if not answer:            bm = await self.bot.say(f':grey_question: | {ctx.message.author.mention} No answer provided. '                                    f'Answer with `,a %answer%`')            await asyncio.sleep(self.timeout)            await self.bot.delete_message(bm)            await self.bot.delete_message(ctx.message)            return        if answer.lower() not in [str(server.q['options']['op1']).lower(), str(server.q['options']['op2']).lower(),                                  str(server.q['options']['op3']).lower(), str(server.q['options']['op4']).lower()]:            bm = await self.bot.say(f':exclamation: | {ctx.message.author.mention} Only one of the four options '                                    f'are accepted. No numbers.')            await asyncio.sleep(self.timeout)            await self.bot.delete_message(bm)            await self.bot.delete_message(ctx.message)            return        print('{} in {} is trying to answer "{}" with answer "{}"'.format(ctx.message.author, ctx.message.server,                                                                          server.q['question'], answer))        # return if the user already answered        if ctx.message.author.id in server.already_answered:            print("{} already answered. ignoring...".format(ctx.message.author))            bm = await self.bot.say(f":bangbang: | {ctx.message.author.mention} You already used up your answer.")            await asyncio.sleep(self.timeout)            await self.bot.delete_message(bm)            await self.bot.delete_message(ctx.message)            return        # add the user to the list of already answered        server.already_answered.append(ctx.message.author.id)        # if the answer is correct, and this is the first user to answer correctly        if server.accept and answer.lower() == str(server.q['answer']).lower():            server.accept = False            print("{} answered correctly.".format(str(ctx.message.author)))            print("-" * 12)            # add 10 points to the user and write it immediately            user.add_correct()            await self.bot.say(f":white_check_mark: | {ctx.message.author.mention} Congratulations! You got it! "                               f"10 points!")            # throw the question off this server's stack            done = server.nextquestion()            # if the server's stack is out of questions            if done:                print("Out of questions. displaying scoreboard...", end = ' ')                embed = server.getscoreboard(ctx)                await self.bot.say(":no_entry: That's all I have, folks! :no_entry:", embed = embed)                server.resetquestions()                print("Scoreboard displayed.")                print('-' * 12)            server.accept = True        # if the answer is correct, but this isn't the first user to answer correctly - the question still isn't thrown.        # believe me, it happened.        elif answer.lower() == str(server.q['answer']).lower():            print("{} answered correctly, but was too slow!".format(ctx.message.author))            bm = await self.bot.say(":clock2: | Too slow, {}!".format(ctx.message.author.mention))            await asyncio.sleep(self.timeout)            await self.bot.delete_message(bm)            await self.bot.delete_message(ctx.message)        # if neither of the above are it, the answer must be wrong.        else:            user.add_incorrect()            print("{} answered incorrectly.".format(str(ctx.message.author)))            bm = await self.bot.say(":x: | Wrong answer, {}.".format(ctx.message.author.mention))            await asyncio.sleep(self.timeout)            await self.bot.delete_message(bm)            await self.bot.delete_message(ctx.message)    @commands.command(pass_context = True, aliases = ['leaderboard', 'board'])    async def scoreboard(self, ctx):        """        Show everyone's score.        """        server = getserver(self.serverdict, ctx)        print("{} in {} is trying to get the scoreboard...".format(ctx.message.author, ctx.message.server), end = ' ')        # does exactly what it says on the tin - gets the scoreboard, an embed.        embed = server.getscoreboard(ctx)        await self.bot.say(embed = embed)        print("Scoreboard displayed.")    @commands.command(pass_context = True, aliases = ['points'])    async def score(self, ctx):        """        Get a user's points.        You may check someone else's score by mentioning them, such as: ,score *mention*        """        if len(ctx.message.mentions) > 0:            user = getuser(self.serverdict, ctx, mentions = ctx.message.mentions[0])        else:            user = getuser(self.serverdict, ctx)        await self.bot.say("{} has {} points.".format(user.mention, user.points))def setup(bot):    x = TriviaCommands(bot)    bot.add_cog(x)