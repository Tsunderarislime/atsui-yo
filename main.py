import discord as ds
from discord.ext import commands, tasks
import yaml
import datetime as dt
from utils import *

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
        channel = self.bot.get_channel(config['channel'])
        weather = get_weather(config['keys']['weatherstack'], config['location'])
        forecast = next(iter(weather['forecast']))
        
        #Cool embed box to send
        embed = ds.Embed(title='Weather Report',
                         description='Good morning Sensei! Here is today\'s weather report.',
                         color=ds.Color.blue()
                         )
        embed.set_thumbnail(url=weather['current']['weather_icons'][0])
        current = str(weather['current']['temperature']) + '°C, ' + weather['current']['weather_descriptions'][0]
        embed.add_field(name='Current Weather', value=current, inline=False) #Current temperature and conditions
        high = str(weather['forecast'][forecast]['maxtemp']) + '°C'
        low = str(weather['forecast'][forecast]['mintemp']) + '°C'
        embed.add_field(name='High', value=high, inline=True) #Daily max
        embed.add_field(name='Low', value=low, inline=True) #Daily min

        await channel.send(embed=embed)

        #Begin distortion when the max temperature exceeds the specified threshold >10%
        #Otherwise, play the sound without any distortions
        if weather['forecast'][forecast]['maxtemp'] > (config['threshold'] * 1.1):
            distort_wav('atsui-yo.wav', 'distorted.wav', config['threshold'], weather['forecast'][forecast]['maxtemp'])
            await channel.send(file=ds.File('distorted.wav'))
        elif weather['forecast'][forecast]['maxtemp'] > config['threshold']:
            await channel.send(file=ds.File('atsui-yo.wav'))
    


#All is good, run the bot
bot.run(config['keys']['bot'])
