import os
import time

#Any exit code that isn't 0 means start/restart the bot
exit_code = 1

while exit_code != 0:
    #Run the bot like this so that updates to the config can be seen live
    exit_code = os.system('python main.py')
    time.sleep(3)
    print(exit_code)
