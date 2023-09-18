from random import choice
import requests
import re

#Get one of four videos, either by choice or randomly depending on what was entered in the command
def atsui(n):
    if n < 0: #When nothing is entered, n = -1 is passed
        level = choice([1, 2, 3, 4])
    else:
        level = n

    match level:
        case 1:
            video = '[⠀](https://files.catbox.moe/0omoql.mp4)'
        case 2:
            video = '[⠀](https://files.catbox.moe/vzgv8j.mp4)'
        case 3:
            video = '[⠀](https://files.catbox.moe/dz1vxd.mp4)'
        case 4:
            video = '[⠀](https://files.catbox.moe/7v515c.mp4)'

    return video

#Get a random Hoshino / Hoshino (Swimsuit) voice line from the Blue Archive wiki
def voice():
    #Choose between two Hoshino variants, then choose a random voice line from the Blue Archive wiki
    hoshino = choice(['Hoshino', 'Hoshino_%28Swimsuit%29'])
    wiki = requests.get('https://bluearchive.wiki/wiki/' + hoshino + '/audio')
    link = choice(re.findall('src="//static\.miraheze\.org/bluearchivewiki/+./[0-9a-f]+/' + hoshino + '_+\w+.ogg"' , str(wiki.content)))
    
    #Get the voice line direct link
    wiki = requests.get('https:' + link[5:-1])
    #Write the file to voice.ogg, the contents of link is the ogg file in byte format
    with open('voice.ogg', 'wb') as v:
        v.write(wiki.content)