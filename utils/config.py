import yaml
import discord as ds

'''
====================================================

    Read and write functions

====================================================
'''

#Load in the config
def load_config():
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
        f.close()
    
    return config

#Write to the config
def write_config(cfg):
    with open('config.yml', 'w') as f:
        config = yaml.dump(cfg, f)
        f.close()
    

'''
====================================================

    Information functions

====================================================
'''
#Get help with command usage, called when no arguments are passed in ^config
def config_help():
    embed = ds.Embed(title='📋 Config Command Usage 📋',
        description='`^config` summons this text box.\nUse `^config info` to see the view the current config',
        color=ds.Color.magenta()
    )
    embed.add_field(name='Channel to Report', value='`^config channel <CHANNEL ID>`', inline=False)
    embed.add_field(name='Meteo URL (Use `^meteo` for more info)', value='`^config meteo <METEO URL>`', inline=False)
    embed.add_field(name='Threshold for Audio Files (°C)', value='`^config threshold <LOWER> <MIDDLE> <UPPER>`', inline=False)
    embed.add_field(name='Time for Daily Report (UTC)', value='`^config time <HOUR> <MINUTE>`', inline=False)

    return embed

#Get help with command usage, called when no arguments are passed in ^config
def config_info(config, title, colour):
    embed = ds.Embed(title=title,
        color=colour
    )
    embed.add_field(name='Channel to Report', value='<#' + str(config['channel']) + '> (' + str(config['channel']) + ')', inline=False)
    embed.add_field(name='Meteo URL (Use `^meteo` for more info)', value=config['meteo'], inline=False)
    embed.add_field(name='Threshold for Audio Files (°C)', value=str(config['threshold']), inline=False)
    embed.add_field(name='Time for Daily Report (UTC)', value=str(config['time']['hour']).zfill(2) + ':' + str(config['time']['minute']).zfill(2), inline=False)

    return embed


'''
====================================================

    Config modification functions

====================================================
'''
#Change the channel that the bot posts the weather reports to
def config_channel(id):
    config = load_config()
    config['channel'] = int(id)
    write_config(config)

#Change the Open-Meteo Forecast API URL to a different location
def config_meteo(url):
    config = load_config()
    config['meteo'] = url
    write_config(config)

#Change the thresholds for the audio clips that get sent in the daily report
def config_threshold(low, mid, hi):
    config = load_config()
    config['threshold'] = [int(low), int(mid), int(hi)]
    write_config(config)

#Change the time of day that the daily report is sent out
def config_time(hour, minute):
    #Bit more complicated since there are constraints. Hours in [0, 24), Minutes in [0, 60)
    h = int(hour)
    m = int(minute)

    #Assert the values, errors will be caught in the calling function
    assert (h >= 0) and (h < 24)
    assert (m >= 0) and (m < 60)

    config = load_config()
    config['time']['hour'] = h
    config['time']['minute'] = m
    write_config(config)

