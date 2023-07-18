import yaml
import discord as ds

'''
====================================================

    Read and write functions

====================================================
'''

#Load in the config
def load_config():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        f.close()
    
    return config

#Write to the config
def write_config(cfg):
    with open('config.yaml', 'w') as f:
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
        description='`^config` summons this information box.\nUse `^config info` to view the current config',
        color=ds.Color.magenta()
    )
    embed.add_field(name='Channel to Report', value='`^config channel <CHANNEL ID>`', inline=False)
    embed.add_field(name='Meteo URL or (Latitude/Longitude) (Use `^meteo` for more info)', value='`^config meteo <METEO URL> OR ^config meteo <LAT> <LON>`', inline=False)
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
    embed.add_field(name='Latitude/Longitude', value='(' + str(config['coord']['latitude']) + ', ' + str(config['coord']['longitude']) + ')', inline=False)
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
def config_meteo(*args):
    #More complicated, as it can take a URL or a set of (lat, lon) coordinates
    assert len(args) in [1, 2]
    config = load_config()

    if len(args) == 1:
        #Set up link and parameters for writing latitude and longitude to the config, will also catch bad links and return an error
        _, params = args[0].split('?') #First half is http://.../forecast?, not needed in this part
        params = params.split('&') #Parameters in the link are separated by '&'

        config['meteo'] = args[0] #Set meteo link as the link passed through
        config['coord']['latitude'] = float(params[0][9:]) #latitude=<float>
        config['coord']['longitude'] = float(params[1][10:]) #longitude=<float>
    else:
        #If two parameters are passed, it's assumed it's LATITUDE then LONGITUDE
        lat = float(args[0]); lon = float(args[1])

        #Assert that the values passed are within bounds
        assert (lat >= -90) and (lat <= 90); assert (lon >= -180) and (lon < 180)
        config['coord']['latitude'] = lat; config['coord']['longitude'] = lon

        #Now to write these values to the meteo URL
        http, params = config['meteo'].split('?')
        params = params.split('&')

        #Modify the latitude and longitude values in the URL
        params[0] = params[0][:9] + str(lat); params[1] = params[1][:10] + str(lon)

        #Reconstruct and write the updated URL to the config
        config['meteo'] = http + '?' + params[0] + ''.join(['&' + params[i] for i in range(1, len(params))])

    write_config(config)

#Change the thresholds for the audio clips that get sent in the daily report
def config_threshold(low, mid, hi):
    config = load_config()
    config['threshold'] = [int(low), int(mid), int(hi)]
    write_config(config)

#Change the time of day that the daily report is sent out
def config_time(hour, minute):
    #Bit more complicated since there are constraints. Hours in [0, 24), Minutes in [0, 60)
    h = int(hour); m = int(minute)

    #Assert the values, errors will be caught in the calling function
    assert (h >= 0) and (h < 24); assert (m >= 0) and (m < 60)

    config = load_config()
    config['time']['hour'] = h; config['time']['minute'] = m
    write_config(config)

