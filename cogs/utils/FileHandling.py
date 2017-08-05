from json import loads


if '\\' in __file__:
    cwd = '/'.join(__file__.split('\\')[:-1])
else:
    cwd = '/'.join(__file__.split('/')[:-1])


def getFileJson(jsonName):
    '''
    Gets the json file and dumps/returns it.
    '''

    # Reads from the file
    with open(cwd + '/../../botstuff/{}'.format(jsonName)) as a:
        data = a.read()

    # Loads it into a dictionary to return it
    return loads(data)
