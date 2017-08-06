from discord.ext import commands
from discord import Status
from cogs.utils.Permissions import permissionChecker
import os


class OwnerCommands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden = True)
    @permissionChecker(check = "is_owner")
    async def kill(self):
        await self.bot.say("I got whacked. Later, losers. :P")
        await self.bot.change_presence(status = Status.invisible, game = None)
        exit()

    @commands.command(hidden = True)
    @permissionChecker(check = 'is_owner')
    async def rld(self, extension: str):
        if os.path.isfile(os.path.join('./cogs/', extension + '.py')):
            await self.bot.say("Reloading extension **{}**...".format(extension))
            self.bot.unload_extension('cogs.' + extension)
            self.bot.load_extension('cogs.' + extension)
            await self.bot.say("Done!")
        else:
            await self.bot.say("Can't find extension **{}**.".format(extension))


def setup(bot):
    x = OwnerCommands(bot)
    bot.add_cog(x)
