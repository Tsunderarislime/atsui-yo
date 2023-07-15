import discord as ds
from discord.ext import commands

#Load in the token found in token.txt (MODIFY THE FILE SO THAT IT CONTAINS YOUR OWN BOT TOKEN)
with open('token.txt') as f:
    token = f.readline()
    f.close()

#Initialize the Discord client object
intents = ds.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='^', description='TEST', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.load_extension('cogs.atsui')

#All is good, run the bot
bot.run(token)
