from discord.ext import commands
from discord import Status
from cogs.utils.Permissions import permissionChecker

class OwnerCommands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True, hidden = True)
    @permissionChecker(check = "is_owner")
    async def kill(self, ctx):
        await self.bot.say("I got whacked. Later, losers. :P")
        await self.bot.change_presence(status = Status.invisible, game = None)
        exit()

def setup(bot):
    x = OwnerCommands(bot)
    bot.add_cog(x)