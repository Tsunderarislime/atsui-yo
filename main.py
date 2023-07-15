import discord as ds

#Replace this
with open('token.txt') as f:
    token = f.readline()
    f.close()

client = ds.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(token)
