import discord as ds
from discord.ext import commands, tasks
import yaml
import datetime as dt
import requests

#Load in the config
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    f.close()

#Initialize the Discord client object
intents = ds.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='^', description='TEST', intents=intents)

#What to run when readying up
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.add_cog(Atsui(bot))


#Get weather data using the Weatherstack API
#Weatherstack API key and location in the YAML file
def get_weather(key, loc):
    #Parameters to pass into the requests.get()
    params = {
        'access_key': key,
        'query': loc
    }

    #Return a json dictionary containing the weather data
    api_result = requests.get('http://api.weatherstack.com/forecast', params)
    return api_result.json()


#Class that contains the cog which has the daily task loop
class Atsui(commands.Cog):
    #Initialize the task
    def __init__(self, bot):
        self.bot = bot
        self.atsui.start()
    
    #Somehow the cog unloads itself
    def cog_unload(self):
        self.atsui.cancel()

    #The main loop that this bot is centered around
    @tasks.loop(time=dt.time(hour=config['time']['hour'], minute=config['time']['minute'], tzinfo=dt.timezone.utc))
    async def atsui(self):
        #Get the weather data
        weather = get_weather(config['keys']['weatherstack'], config['location'])


#All is good, run the bot
bot.run(config['keys']['bot'])
