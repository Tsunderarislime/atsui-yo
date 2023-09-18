import discord as ds
from discord.ext import commands, tasks
import numpy as np
import time
import datetime as dt
import utils.weather
import utils.info
import utils.fun
from utils.config import *

#Load in the config
config = load_config()

#Timestamp on startup
startup_time = time.time()

#Initialize the Discord client object
intents = ds.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='^', description='ATSUI YO', intents=intents, activity=ds.Game(name="with fire | ^help"))
bot.remove_command('help')
#What to run when readying up
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('----------------------------------------------------')
    await bot.add_cog(Atsui(bot))

'''
================================================

    Commands to shutdown and restart the bot

================================================
'''
#Shutdown and restart commands, requires admin permissions to use
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    print('Invoked shutdown command')
    await ctx.send('Sensei! I\'m gonna go to sleep now.')
    await bot.close() #This returns an exit code of 0 for the sake of run.py

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def restart(ctx):
    print('Invoked restart command')
    await ctx.send('Sensei! I\'ll be right back!')
    exit(1) #This will raise an exception from asyncio, but it will still close and restart the bot properly


#Handle use of the commands without admin permissions
@shutdown.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('Sensei, you need to have administrator permissions for me to shutdown!')

@restart.error
async def restart_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('Sensei, you need to have administrator permissions for me to restart!')


'''
================================================

    Command to configure the bot

================================================
'''
#^config <what_to_config> <arg1> <arg2> ...
@bot.command(name='config', alias='configure')
@commands.has_permissions(administrator=True)
async def configure(ctx, *args):
    #Send help dialogue if not enough arguments are passed
    if len(args) < 1:
        await ctx.send(embed=config_help())
    elif args[0] in ['info', 'clear', 'channel', 'meteo', 'threshold', 'time']:
        #Info box about current configuration
        if args[0] == 'info':
            await ctx.send(embeds=[config_info(config, '▶️ The Config Currently in Use ▶️', ds.Color.green()),
                config_info(load_config(), '🔁 The Config After Restart 🔁', ds.Color.green())
            ])
            return
        
        run = 'config_' + args[0] + str(args[1:])
        try:
            exec(run)
            await ctx.send('Sensei! I have modified `' + args[0] + '` in the config!\nI recommend running `^restart` to apply this new change.')
        except Exception as e:
            print(e)
            await ctx.send('Sensei, did you give me the right parameters?\nPlease use `^config` for a quick command usage guide.')
    else:
        await ctx.send('Invalid command `' + args[0] + '`')
            
#Handle use of the commands without admin permissions
@configure.error
async def configure_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('Sensei, you need to have administrator permissions to change my config!')

'''
================================================

    Commands for miscellaneous information

================================================
'''
#Command to list all of the commands
@bot.command()
async def help(ctx):
    embed = utils.info.help()
    await ctx.send(embed=embed)

#Command to show the main GitHub repository
@bot.command()
async def github(ctx):
    embed = utils.info.github()
    await ctx.send(embed=embed)

#Command to send embed with links to Open-Meteo Forecast API
@bot.command()
async def meteo(ctx):
    embed = utils.info.meteo()
    await ctx.send(embed=embed)

#Command to see how long the bot has been running for since the last restart
@bot.command()
async def uptime(ctx):
    embed = utils.info.uptime(startup_time)
    await ctx.send(embed=embed)

'''
================================================

    Commands for fun

================================================
'''
#Command to manually send an ATSUI YO video. Choose from levels 1-4 of increasing distortion or enter nothing to send a random one
@bot.command()
async def atsui(ctx, *args):
    if len(args) < 1:
        video = utils.fun.atsui(-1) #The function will handle n = -1 as random
    else:
        try: #Ensure the argument is an integer, 1, 2, 3, 4
            n = int(args[0])
            assert n in [1, 2, 3, 4]
            video = utils.fun.atsui(n)
        except Exception as e:
            print(e)
            await ctx.send('Sensei, did you give me the right parameters?\nIt should be an integer from 1-4.')
            return
    
    await ctx.send(video) #ATSUI YO

#Command to randomly send a Hoshino or Hoshino (Swimsuit) voice line, straight from the Blue Archive Wiki
@bot.command()
async def voice(ctx):
    utils.fun.voice()
    await ctx.send(content='Hey Sensei! I have something to say to you!', file=ds.File('voice.ogg'))

'''
================================================

    Commands for weather reports on demand

================================================
'''
#Command to get 12 hour temperature forecast from current hour
@bot.command()
async def current(ctx):
    #Generate the current 12 hour forecast
    async with ctx.typing():
        weather = utils.weather.get_weather(config['meteo'])
        greeting, embed = utils.weather.current(weather, ds.Color.blue(), config['location']) #current() also returns a greeting

    await ctx.send(content=greeting + '\nHere is the current weather forecast!', embed=embed)

#Command to get n day weather forecast (1-7 days), weather conditions, high/low temperatures. 6-7 days can look weird on smaller screens
@bot.command()
async def forecast(ctx, n):
    #Ensure n is the right type and within bounds
    try:
        days = int(n)
        assert (days >=1) & (days <= 7)
    except Exception as e:
        print(e)
        await ctx.send('Sensei, did you give me the right parameter?\nIt should be an integer from 1-7.')
        return
    
    #Generate the current n day forecast
    async with ctx.typing():
        weather = utils.weather.get_weather(config['meteo'])
        embed = utils.weather.forecast(weather, days, ds.Color.blue(), config['location'])
            
    await ctx.send(content='Hey Sensei!\nHere is the ' + str(days) + ' day forecast you requested!', embed=embed)

@forecast.error
async def forecast_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Sensei! I need to know how many days you want in your forecast! [1-7]')

#Class that contains the cog which has the daily task loop
class Atsui(commands.Cog):
    #Initialize the task
    def __init__(self, bot):
        self.bot = bot
        self.atsui.start()
    
    #Somehow the cog unloads itself
    def cog_unload(self):
        self.atsui.cancel()

    #The main loop to send the daily reports
    @tasks.loop(time=dt.time(hour=config['time']['hour'], minute=config['time']['minute'], tzinfo=dt.timezone.utc))
    async def atsui(self):
        #Get the weather data
        channel = self.bot.get_channel(config['channel'])
        weather = utils.weather.get_weather(config['meteo'])
        
        #Determine the colour of the embed box and which sound file to post
        match np.searchsorted(config['threshold'], weather['daily']['temperature_2m_max'][0], side='right'):
            case 0: #Daily high is less than the threshold entirely
                colour=ds.Color.green()
                greeting = '悪くないぞ。'
                video = '[⠀](https://files.catbox.moe/0omoql.mp4)'
            case 1: #Daily high made the lower half of the threshold
                colour=ds.Color.yellow()
                greeting = '*あっつい…*\n*暑くて干からびそう…*\n*動いてないのに暑いよ～…*'
                video = '[⠀](https://files.catbox.moe/vzgv8j.mp4)'
            case 2: #Daily high made the upper half of the threshold
                colour=ds.Color.orange()
                greeting = '## *あっつい…*\n## *暑くて干からびそう…*\n## *動いてないのに暑いよ～…*'
                video = '[⠀](https://files.catbox.moe/dz1vxd.mp4)'
            case 3: #Daily high exceeded the upper bound of the threshold
                colour=ds.Color.red()
                greeting = '# *あっつい…*\n# *暑くて干からびそう…*\n# *動いてないのに暑いよ～…*'
                video = '[⠀](https://files.catbox.moe/7v515c.mp4)'
        
        #Construct the current weather embed
        _, embed = utils.weather.current(weather, colour, config['location'])

        #In the case that the bot wants to clear its own messages.
        #Highly recommend if it sends messages in its own separate channel, as the Discord desktop client can lag with the amount of emojis it needs to show
        if config['clear']:
            n = await channel.purge(limit=8, check=is_me, reason='Bot cleaning its own messages', bulk=True)
            print('Deleted ' + str(len(n)) + ' bot message(s)')

        #Send the weather report
        await channel.send(content=greeting, embed=embed)
        #Send the funny video
        await channel.send(content=video, silent=True)

#Check if messages were sent by the bot
def is_me(m):
    return m.author.id == bot.user.id

#All is good, run the bot
bot.run(config['key'])