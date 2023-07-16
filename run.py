import os
import time

#Exit code 1 means start/restart
exit_code = 1

while exit_code == 1:
    #Run the bot like this so that updates to the config can be seen live
    exit_code = os.system('python main.py')
    time.sleep(3)
    print(exit_code)
