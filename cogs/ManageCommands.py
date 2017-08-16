import re
import os
from sys import exc_info, argv, exit, executable
from traceback import format_exception
from discord.ext import commands
from discord import Status
from cogs.utils.Permissions import permissionChecker
from bot import __version__


# criteria for determining who can access owner only commands
perm = 'is_owner'


class ManageCommands:
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.cogdict = {}

        # Smart™ cog shortcut generation, depending on the capital letters in the file name.
        # such as: TriviaCommands.py has a shortcut of tc, and StaffCommands.py has a shortcut of sc, and so on.

        # for each file in ./cogs/:
        for i in os.listdir('./cogs/'):
            if os.path.isfile(os.path.join('./cogs/' + i)):
                # remove all small letters, and the dot(for the .py extension)
                x = re.sub('[a-z.]', '', i).lower()
                # see if there is something already registered by that shortcut. if there is, add a dash to the shortcut
                # if there isn't, it'll raise KeyError, where nothing will happen.
                try:
                    if self.cogdict[x]:
                        x += '-'
                except KeyError:
                    pass
                # insert it into the dictionary, with the shortcut being `x`, and the cog name being the filename
                # without .py.
                self.cogdict[x] = i.split('.')[0]

    @commands.command(aliases = ['delet'])
    @permissionChecker(check = perm)
    async def kill(self):
        """
        Kills the bot. Owner only.
        """
        await self.bot.say("I got whacked. Later, losers. :P")

        # set status to invisible
        await self.bot.change_presence(status = Status.invisible, game = None)
        exit()

    @commands.command(aliases = ['reload'])
    @permissionChecker(check = perm)
    async def rld(self, extension: str):
        """
        Reloads a cog. Owner only.
        """

        # check if it's a shortcut
        try:
            extension = self.cogdict[extension]
        except KeyError:
            pass

        # check if it's an actual cog, and if it is, unload it, and then load it.
        if os.path.isfile(os.path.join('./cogs/', extension + '.py')):
            await self.bot.say("Reloading extension **{}**...".format(extension))
            self.bot.unload_extension('cogs.' + extension)
            self.bot.load_extension('cogs.' + extension)
            await self.bot.say("Done!")
        else:
            await self.bot.say("Can't find extension **{}**.".format(extension))

    @commands.command()
    @permissionChecker(check = perm)
    async def rldall(self):
        """
        Reloads all cogs. Owner only.
        """
        for i in os.listdir('./cogs/'):
            if os.path.isfile(os.path.join('./cogs/', i)):
                extension = i.split('.')[0]
                await self.bot.say("Reloading extension **{}**...".format(extension))
                self.bot.unload_extension('cogs.' + extension)
                self.bot.load_extension('cogs.' + extension)
        await self.bot.say("Done!")

    @commands.command(aliases = ['v'])
    async def version(self):
        """
        Display the bot's version.
        """
        await self.bot.say("I am at version {}.".format(__version__))

    @commands.command()
    @permissionChecker(check = perm)
    async def ev(self, *, content):
        """
        Evaluate python expression.
        """
        # try to evaluate, and in case of an error, print the traceback instead.
        try:
            output = eval(content)
        except Exception:
            type_, value_, traceback_ = exc_info()
            ex = format_exception(type_, value_, traceback_)
            output = ''.join(ex)

        await self.bot.say('```python\n{}```'.format(output))

    @commands.command()
    @permissionChecker(check = perm)
    async def restartbot(self):
        """
        Restarts the bot. Owner only.
        :return:
        """
        msg = await self.bot.say("Restarting...")
        await self.bot.change_presence(status = Status.dnd, game = None)

        # calls the command to start the bot, and passes the message's id, so the bot can edit it when it starts.
        os.execl(executable, *([executable] + [argv[0], argv[1]] + [msg.id, msg.channel.id]))

def setup(bot):
    x = ManageCommands(bot)
    bot.add_cog(x)
