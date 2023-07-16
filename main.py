import discord as ds
from discord.ext import commands, tasks
import numpy as np
import datetime as dt
import utils.weather
from utils.config import *

#Load in the config
config = load_config()

#Initialize the Discord client object
intents = ds.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='^', description='ATSUI YO', intents=intents, activity=ds.Game(name="with fire"))
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
    print('Shutting down...')
    await ctx.send('Shutting down the bot...')
    await bot.close() #This returns an exit code of 0 for the sake of run.py

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def restart(ctx):
    print('Restarting...')
    await ctx.send('Restarting...')
    exit(1) #This causes a bunch of errors to pop up in the terminal window, but seems to function fine otherwise


#Handle use of the commands without admin permissions
@shutdown.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('Sorry, you do not have the necessary permissions to shutdown the bot.')

@restart.error
async def restart_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('Sorry, you do not have the necessary permissions to restart the bot.')


'''
================================================

    Commands to configure the bot

================================================
'''
#^config <what_to_config> <arg1> <arg2> ...
@bot.command(name='config', alias='configure')
@commands.has_permissions(administrator=True)
async def configure(ctx, *args):
    #Send help dialogue if not enough arguments are passed
    if len(args) < 1:
        await ctx.send(embed=config_help())
    elif args[0] in ['info', 'channel', 'meteo', 'threshold', 'time']:
        #Info box about current configuration
        if args[0] == 'info':
            await ctx.send(embed=config_info(config, 'The Config Currently in Use', ds.Color.dark_green()))
            await ctx.send(embed=config_info(load_config(), 'The Config After Restart', ds.Color.green()))
            return
        
        run = 'config_' + args[0] + str(args[1:])
        print(run)
        try:
            exec(run)
            await ctx.send('Successfully modified `' + args[0] + '` in the config.\nIt is recommended that you run `^restart` to apply this new change.')
        except Exception as e:
            print(e)
            await ctx.send('There appears to be an issue with the parameters being passed.\nPlease use `^config` for a quick command usage guide.')
    else:
        await ctx.send('Invalid command `' + args[0] + '`')
            
#Handle use of the commands without admin permissions
@configure.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('Sorry, you do not have the necessary permissions to change the bot configuration.')


#Commands to send embed with links to Open-Meteo Forecast API
@bot.command()
async def meteo(ctx):
    meteo = ds.Embed(title='Open-Meteo Forecast API',
        url='https://open-meteo.com/en/docs',
        description='Click the link above to access the Open-Meteo Forecast API. The URL generated from the API is used to pull weather forecast data for this bot.'
    )
    meteo.set_thumbnail(url='https://avatars.githubusercontent.com/u/86407831?s=200&v=4')

    await ctx.send(embed=meteo)


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
        weather = utils.weather.get_weather(config['meteo'])
        
        #Determine the colour of the embed box and which sound file to post
        match np.searchsorted(config['threshold'], weather['daily']['temperature_2m_max'], side='right'):
            case 0: #Daily high is less than the threshold entirely
                embed = utils.weather.weather_embed(weather, colour=ds.Color.green())
                audio = 'audio/not-bad.mp3'
            case 1: #Daily high made the lower half of the threshold
                embed = utils.weather.weather_embed(weather, colour=ds.Color.yellow())
                audio = 'audio/atsui-yo.mp3'
            case 2: #Daily high made the upper half of the threshold
                embed = utils.weather.weather_embed(weather, colour=ds.Color.orange())
                audio = 'audio/atsui-yooo.mp3'
            case 3: #Daily high exceeded the upper bound of the threshold
                embed = utils.weather.weather_embed(weather, colour=ds.Color.red())
                audio = 'audio/atsui-yooooo.mp3'
        
        #Send the weather report
        await channel.send(embed=embed, file=ds.File(audio))


#All is good, run the bot
bot.run(config['key'])
