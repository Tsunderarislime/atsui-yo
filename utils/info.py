import discord as ds
import time

#List all of the commands
def help():
    embed = ds.Embed(title='💡 Help 💡',
        description='Hey Sensei! Here\'s a list of commands!',
        color=ds.Color.green()
    )
    embed.add_field(name='Admin 🔑', value='- `^config`\n- `^restart`\n- `^shutdown`', inline=True)
    embed.add_field(name='Information ℹ️', value='- `^help`\n- `^github`\n- `^meteo`\n- `^uptime`', inline=True)
    embed.add_field(name='Weather ☀️', value='- `^current`\n- `^forecast`', inline=False)

    return embed

#Github repository links
def github():
    embed = ds.Embed(title='GitHub Repository',
        url='https://github.com/Tsunderarislime/atsui-yo',
        description='Hey Sensei! Here\'s the link to the main GitHub repository!',
        color=ds.Color.green()
    )
    embed.set_image(url='https://i.imgur.com/y6ltubQ.png')

    return embed

#Guide for Open-Meteo API link creation
def meteo():
    embed = ds.Embed(title='Open-Meteo Forecast API',
        url='https://open-meteo.com/en/docs',
        description='Hey Sensei! Click the link above to access the Open-Meteo Forecast API. The URL generated from the API is used to pull weather forecast data.',
        color=ds.Color.green()
    )
    embed.set_thumbnail(url='https://avatars.githubusercontent.com/u/86407831?s=200&v=4')
    embed.add_field(name='Guide on what parameters to choose', value='https://github.com/Tsunderarislime/atsui-yo/wiki/Open%E2%80%90Meteo-Forecast-API-URL', inline=False)
    embed.add_field(name='', value='Once you have obtained the Forecast API URL, you can simply change locations by using:\n`^config meteo <LAT> <LON>`')

    return embed

#Uptime of the bot in days, hours, minutes, and seconds
def uptime(t):
    #Get time difference since startup time 't'
    elapsed = int(round(time.time() - t, 0))
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

    return embed