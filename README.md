# triviabot
A discord bot

Not hosted; not open for public usage. You are, however, welcome to host your own version, or to copy the trivia-related cogs into your bot.

Contact me on discord: `ala#2941`

# Changelog

### Version 1.0

  - Initial release.
  
### Version 1.1

  - TriviaCommands.py:
    - Combined question jsons into one json file.
    - Replaced pickling `Question` objects with json-ing question dictionaries.
    - Removed `Question` class.
    - Removed some useless attributes from the `User` class.
    - Rewritten the `Server` class.
    - Removed `TriviaCommands`' static method `bypassquestion` in favour of `Server`'s `nextquestion`.
    - Added `User.add_correct()` and `User.add_incorrect()`.
    - Changed getscoreboard to use member.name instead of member.display_name.
  - process_files.py:
    - Rewrote the entire thing to accomodate single json file.
    - Usage help: Place all questions.json in `./botstuff/jsonfiles`. Rename if necessary. Run `process_files.py`,
      and they'll automatically be added to the main `questions.json` file.
      
#### Version 1.1.1

  - TriviaCommands.py:
    - Returned bot to working order.
    - Made bot retell the question if it was already asked with `^trivia` and `^starttrivia` was invoked.
    - Bot went bonkers if `^starttrivia` was called several times. Now it only runs one instance of `^starttrivia` at a time.
    - Bot forgot player scores if restarted. Fixed.
  - OwnerCommands.py:
    - Added ^version command.
    - Added shortcuts for cog-reloading. ^rld tc for TriviaCommands, and ^rld gc for OwnerCommands.
  - Discovered aliases. Went bonkers.
  
### Version 1.2

  - Rewrote a great deal of code.
  - TriviaCommands.py:
    - Now only contains user-specific commands
  - HelperFunctions.py:
    - Contains User and Server, along side some helper functions.
  - StaffTrivia.py:
    - Contains staff-specific commands.
  - Changed prefix to `,`.
  
#### Version 1.2.1

  - HelperFunctions.py:
    - Fixed an error which occurs if the server's directory did not exist(Yes, I know, should've seen this coming).
  - StaffCommands.py:
    - `,resetscore` can now be used to reset someone else's score by mentioning them.
    
#### Version 1.2.2

  - TriviaCommands.py:
    - Bot now notifies if a user tries to answer after already using up their answer.
    - Bot now processes concurrent answers more efficiently; processes them all, but only one gets into the
      "correct answer" if statement, as opposed to processing them one at a time.
    - Bot no longer accepts empty `,a` commands.
  - Added README.md.
  
#### Version 1.2.3

  - TriviaCommands.py:
    - Removed some redundant checks in `,a`.
    
#### Version 1.2.4

  - HelperFunctions.py:
    - Hopefully™ fixed the `User` class's `mention` property.
    
#### Version 1.2.5

  - Better logging.
  - ManageCommands.py:
    - Retroactive cog reload shortcuts; they depend on the capital letters in a given file name. For example, ManageCommands.py has a shortcut of `mc`.

#### Version 1.2.6

  - Fixed the dumbest error in existence.
  - Added the `,ev` command. May be useful in debugging. Owner only, of course.
  
#### Version 1.2.7

  - Minor message fixes.

#### Version 1.2.8

  - I have no Idea what I did, but bugs were fixed. Many bugs.

### Version 1.3
  - Spam-proofing fixes
    - Rewrote `,a`, bot now only accepts written answers(read: no option-number answers) and only processes those which are actually one of the answers. Anything else is ignored.
    - Overhauled the point system. A user now gets 10 points for each correct answer, and loses 5 points for each incorrect answer, as to discourage spamming.
  - Added comments to the code.
  - The `dispense` and `getscoreboard` functions are now Server methods.
  - Added `,restartbot` command. Does what you expect it to.
  - Bot now automatically removes all incorrect messages after a 2 second timeout.
  - Bot now uses emoji(May I be forgiven for this) to indicate the response at a glace.
