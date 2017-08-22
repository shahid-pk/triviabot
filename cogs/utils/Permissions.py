from discord.ext import commands
from .FileHandling import getFileJson


def permcheck(ctx, **kwargs):
    check = kwargs.get('check', 'send_messages')
    compare = kwargs.get('compare', False)
    owners = kwargs.get('owners', [])
    channel = ctx.message.channel
    server = ctx.message.server
    author = ctx.message.author
    settings = getFileJson('Config.json')

    # Checks if it's an owner
    if author.id in settings['Owner IDs'] + owners:
        return True
    # Sees if the author is the server owner
    elif server.owner.id == author.id:
        return True
    elif check == 'is_owner':
        return False

    # Checks if it's a PM
    if server is None:
        return False

    # Looks at the person to compare against
    if compare:

        # Get the member mentions in the message (excluding the bot)
        mentions = [i for i in ctx.message.mentions if i.id != ctx.bot.user.id]

        # Check that it's not empty
        if not mentions:
            return False

        # Pretty much just return false if they have a higher top role, otherwise continue
        if author.top_role.position <= mentions[-1].top_role.position:
            return False

    # Check that the user has permission to actually do what they want to
    permissionsInChannel = channel.permissions_for(author)
    if getattr(permissionsInChannel, 'administrator'):
        return True
    z = getattr(permissionsInChannel, check)
    if z:
        return z
    else:
        return False


def permissionChecker(**kwargs):
    """Checks permissions based on ctx and some kwargs

    Parameters ::
        check : str
            The permssion check that the bot will look for
        compare : bool = None
            The type of tag that the bot will look to compare against
            Defaults to None, and will just return whether or not the user has permission
        owners : list (of str)
            Lets the bot add additional owners to just a command
    """

    predicate = permcheck

    return commands.check(predicate)


def hasRoles(**kwargs):
    def predicate(ctx):
        return len(ctx.message.author.roles) != 1
    return commands.check(predicate)
