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
    embed = ds.Embed(title='💡 Help 💡',
        description='Hey Sensei! Here\'s a list of commands!',
        color=ds.Color.green()
    )
    embed.add_field(name='Weather ☀️', value='- `^current`\n- `^forecast`', inline=True)
    embed.add_field(name='Information ℹ️', value='- `^help`\n- `^github`\n- `^meteo`\n- `^uptime`', inline=True)
    embed.add_field(name='Admin 🔑', value='- `^config`\n- `^restart`\n- `^shutdown`', inline=False)

    await ctx.send(embed=embed)

#Command to send embed with links to Open-Meteo Forecast API
@bot.command()
async def meteo(ctx):
    meteo = ds.Embed(title='Open-Meteo Forecast API',
        url='https://open-meteo.com/en/docs',
        description='Hey Sensei! Click the link above to access the Open-Meteo Forecast API. The URL generated from the API is used to pull weather forecast data.',
        color=ds.Color.green()
    )
    meteo.set_thumbnail(url='https://avatars.githubusercontent.com/u/86407831?s=200&v=4')
    meteo.add_field(name='Guide on what parameters to choose', value='https://github.com/Tsunderarislime/atsui-yo/wiki/Open%E2%80%90Meteo-Forecast-API-URL', inline=False)
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
    embed.set_image(url='https://i.imgur.com/y6ltubQ.png')

    await ctx.send(embed=embed)

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
                video = 'https://files.catbox.moe/0omoql.mp4'
            case 1: #Daily high made the lower half of the threshold
                colour=ds.Color.yellow()
                greeting = '*あっつい…*\n*暑くて干からびそう…*\n*動いてないのに暑いよ～…*'
                video = 'https://files.catbox.moe/vzgv8j.mp4'
            case 2: #Daily high made the upper half of the threshold
                colour=ds.Color.orange()
                greeting = '## *あっつい…*\n## *暑くて干からびそう…*\n## *動いてないのに暑いよ～…*'
                video = 'https://files.catbox.moe/dz1vxd.mp4'
            case 3: #Daily high exceeded the upper bound of the threshold
                colour=ds.Color.red()
                greeting = '# *あっつい…*\n# *暑くて干からびそう…*\n# *動いてないのに暑いよ～…*'
                video = 'https://files.catbox.moe/7v515c.mp4'
        
        #Construct the current weather embed
        _, embed = utils.weather.current(weather, colour, config['location'])

        #Send the weather report
        await channel.send(content=greeting, embed=embed)
        #Send the funny video
        await channel.send(content=video, silent=True)


#All is good, run the bot
bot.run(config['key'])