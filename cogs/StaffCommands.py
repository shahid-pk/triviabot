import os
from discord.ext import commands
from cogs.utils.TriviaBackend import getserver, Server
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
        server.writeconfig()


def setup(bot):
    cog = StaffCommands(bot)
    bot.add_cog(cog)
