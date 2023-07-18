import discord as ds
from discord.ext import commands, tasks
import numpy as np
import time
import datetime as dt
import utils.weather
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
    await ctx.send('Shutting down...')
    await bot.close() #This returns an exit code of 0 for the sake of run.py

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def restart(ctx):
    print('Invoked restart command')
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
    elif args[0] in ['info', 'channel', 'meteo', 'threshold', 'time']:
        #Info box about current configuration
        if args[0] == 'info':
            await ctx.send(embeds=[config_info(config, '▶️ The Config Currently in Use ▶️', ds.Color.green()),
                config_info(load_config(), '🔁 The Config After Restart 🔁', ds.Color.green())
            ])
            return
        
        run = 'config_' + args[0] + str(args[1:])
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

'''
================================================

    Commands for miscellaneous information

================================================
'''
#Command to list all of the commands
@bot.command()
async def help(ctx):
    embed = ds.Embed(title='💡 Help 💡',
        description='Hey Sensei! Here\'s a list of commands!',
        color=ds.Color.green()
    )
    embed.add_field(name='Weather ☀️', value='- `^current`', inline=True)
    embed.add_field(name='Information ℹ️', value='- `^help`\n- `^github`\n- `^meteo`\n- `^uptime`', inline=True)
    embed.add_field(name='Admin 🔑', value='- `^config`\n- `^restart`\n- `^shutdown`', inline=False)

    await ctx.send(embed=embed)

#Command to send embed with links to Open-Meteo Forecast API
@bot.command()
async def meteo(ctx):
    meteo = ds.Embed(title='Open-Meteo Forecast API',
        url='https://open-meteo.com/en/docs',
        description='Click the link above to access the Open-Meteo Forecast API. The URL generated from the API is used to pull weather forecast data for this bot.',
        color=ds.Color.green()
    )
    meteo.set_thumbnail(url='https://avatars.githubusercontent.com/u/86407831?s=200&v=4')
    meteo.add_field(name='Guide on what parameters to choose', value='https://github.com/Tsunderarislime/atsui-yo', inline=False)
    meteo.add_field(name='', value='Once you have obtained the Forecast API URL, you can simply change locations by using:\n`^config meteo <LAT> <LON>`')

    await ctx.send(embed=meteo)

#Command to see how long the bot has been running for since the last restart
@bot.command()
async def uptime(ctx):
    elapsed = int(round(time.time() - startup_time, 0))

    #Get days
    days = elapsed // (24 * 3600); elapsed = elapsed % (24 * 3600)

    #Get hours
    hours = elapsed // 3600; elapsed = elapsed % 3600

    #Get minutes
    minutes = elapsed // 60; elapsed = elapsed % 60

    #Message embed
    embed = ds.Embed(title='⌛ Uptime ⌛',
        color=ds.Color.green()
    )
    embed.add_field(name='Days', value='{d:.0f}'.format(d=days), inline=False)
    embed.add_field(name='Hours', value='{h:.0f}'.format(h=hours), inline=True)
    embed.add_field(name='Minutes', value='{m:.0f}'.format(m=minutes), inline=True)
    embed.add_field(name='Seconds', value='{s:.0f}'.format(s=elapsed), inline=True)

    await ctx.send(embed=embed)

#Command to show the main GitHub repository
@bot.command()
async def github(ctx):
    embed = ds.Embed(title='GitHub Repository',
        url='https://github.com/Tsunderarislime/atsui-yo',
        description='Hey Sensei! Here\'s the link to the main GitHub repository!',
        color=ds.Color.green()
    )
    embed.set_thumbnail(url='https://i.ytimg.com/vi/0BqAlaSXEkE/mqdefault.jpg')

    await ctx.send(embed=embed)

'''
================================================

    Commands for weather reports on demand

================================================
'''
#Command to get 12 hour temperature forecast from current hour
@bot.command()
async def current(ctx):
    #Generate the forecast
    async with ctx.typing():
        weather = utils.weather.get_weather(config['meteo'])

        #Get the greeting and weather
        greeting, embed = utils.weather.current(weather, ds.Color.blue())

    await ctx.send(content=greeting + '\nHere is the current weather report!', embed=embed)

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
                _, embed = utils.weather.current(weather, colour=ds.Color.green())
                greeting = '\n悪くないぞ。'
                video = 'https://raw.githubusercontent.com/Tsunderarislime/atsui-yo/main/video/not-bad.mp4'
            case 1: #Daily high made the lower half of the threshold
                _, embed = utils.weather.current(weather, colour=ds.Color.yellow())
                greeting = '\n*あっつい…*\n*暑くて干からびそう…*\n*動いてないのに暑いよ～…*'
                video = 'https://raw.githubusercontent.com/Tsunderarislime/atsui-yo/main/video/atsui-yo.mp4'
            case 2: #Daily high made the upper half of the threshold
                _, embed = utils.weather.current(weather, colour=ds.Color.orange())
                greeting = '\n## *あっつい…*\n## *暑くて干からびそう…*\n## *動いてないのに暑いよ～…*'
                video = 'https://raw.githubusercontent.com/Tsunderarislime/atsui-yo/main/video/atsui-yooo.mp4'
            case 3: #Daily high exceeded the upper bound of the threshold
                _, embed = utils.weather.current(weather, colour=ds.Color.red())
                greeting = '\n# *あっつい…*\n# *暑くて干からびそう…*\n# *動いてないのに暑いよ～…*'
                video = 'https://raw.githubusercontent.com/Tsunderarislime/atsui-yo/main/video/atsui-yooooo.mp4'

        #Send the weather report
        await channel.send(content=greeting, embed=embed)
        #Send the funny video
        await channel.send(content=video, silent=True)


#All is good, run the bot
bot.run(config['key'])