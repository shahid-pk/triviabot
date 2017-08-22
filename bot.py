#! python3.6
from sys import argv, exc_info
from traceback import format_exception
from discord.ext import commands
import discord
import os

try:
    __version__ = '1.5.2'

    description = \
        """Hey boys, I'm a bot written by your OG Ala to provide you with useless trivia."""

    prefix = ","

    bot = commands.Bot(
        command_prefix = prefix,
        description = description,
    )


    @bot.event
    async def on_ready():
        if len(argv) > 2:
            print('Restarted successfully. \n' + '-' * 12)
        print("Logged in successfully")
        print(bot.user.name)
        print(bot.user.id)
        print("-" * 12)

        # nicely set up the game
        await bot.change_presence(game = discord.Game(name = "{}help".format(prefix)))

        # load all cogs
        for i in os.listdir("./cogs"):
            if os.path.isfile(os.path.join("./cogs", i)):
                i = i.split('.')[0]
                print("Loading extension: {0}".format(i), end = '\r')
                bot.load_extension("cogs.{0}".format(i))
                print("Extension {0} loaded.".ljust(40).format(i))

        # ping in case it was restarted using `,restartbot`
        try:
            if len(argv) > 2:
                msg = await bot.get_message(bot.get_channel(argv[3]), argv[2])
                await bot.edit_message(msg, msg.content + "\nRestarted successfully")
        except IndexError:
            pass

        print("-" * 12)


    if __name__ == '__main__':
        bot.run(argv[1])

except Exception:
    type_, value_, traceback_ = exc_info()
    ex = format_exception(type_, value_, traceback_)
    output = ''.join(ex)

    print(output)
    with open('error.txt', 'w', encoding = 'UTF-8') as f:
        f.write(str(output))
    exit(1)
