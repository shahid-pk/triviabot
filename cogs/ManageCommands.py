from discord.ext import commands
from discord import Status
from cogs.utils.Permissions import permissionChecker
from mein_bot import __version__
import os

perm = 'is_owner'


class ManageCommands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['delet'])
    @permissionChecker(check = perm)
    async def kill(self):
        """
        Kills the bot. Owner only.
        """
        await self.bot.say("I got whacked. Later, losers. :P")
        await self.bot.change_presence(status = Status.invisible, game = None)
        exit()

    @commands.command(aliases = ['reload'])
    @permissionChecker(check = perm)
    async def rld(self, extension: str):
        """
        Reloads a cog. Owner only.
        """
        cogdict = {
            'tc': 'TriviaCommands',
            'mc': 'ManageCommands',
            'sc': 'StaffCommands'
        }
        try:
            extension = cogdict[extension]
        except KeyError:
            pass

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


def setup(bot):
    x = ManageCommands(bot)
    bot.add_cog(x)
