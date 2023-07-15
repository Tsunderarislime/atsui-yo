import discord as ds

#Load in the token found in token.txt (MODIFY THE FILE SO THAT IT CONTAINS YOUR OWN BOT TOKEN)
with open('token.txt') as f:
    token = f.readline()
    f.close()

#Initialize the Discord client object
intents = ds.Intents.default()
intents.message_content = True

client = ds.Client(intents=intents)

#Client event listeners
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


#All is good, run the bot
client.run(token)
