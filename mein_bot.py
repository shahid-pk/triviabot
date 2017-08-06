#!usr/env/bin python
from sys import argv
from discord.ext import commands
import discord
import os

__version__ = '1.0'

description = \
    """TriviaBot"""

bot = commands.Bot(
    command_prefix = "^",
    description = description,
)


@bot.event
async def on_ready():
    print("Logged in successfully")
    print(bot.user.name)
    print(bot.user.id)
    print("-" * 12)

    await bot.change_presence(game = discord.Game(name = "^help"))

    for i in os.listdir("./cogs"):
        if os.path.isfile(os.path.join("./cogs", i)):
            i = i.split('.')[0]
            print("Loading extension: {0}".format(i))
            bot.load_extension("cogs.{0}".format(i))
            print("Extension {0} loaded.".format(i))

    print("-" * 12)


if __name__ == '__main__':
    bot.run(argv[1])
