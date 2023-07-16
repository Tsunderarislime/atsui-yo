import requests
import numpy as np
import datetime as dt
import discord as ds

#Weathercodes, 10, 11, 12, and 13 are not real codes, but I want to use them to substitute the sun in the case of night reports
code = {
    0: 'Sunny ☀️',
    1: 'Mostly Sunny 🌤️',
    2: 'Partly Cloudy ⛅',
    3: 'Overcast ☁️',
    10: 'Clear 🌕',
    11: 'Mostly Clear 🌙',
    12: 'Partly Clear🌙',
    13: 'Overcast ☁️',
    45: 'Foggy 🌫️',
    48: 'Foggy ❄️',
    51: 'Light Drizzle 🌧️',
    53: 'Drizzle 🌧️',
    55: 'Heavy Drizzle 🌧️',
    56: 'Light Drizzle 🌧️',
    57: 'Heavy Drizzle 🌧️',
    61: 'Light Rain 🌧️',
    63: 'Rain 🌧️',
    65: 'Heavy Rain 🌧️',
    66: 'Light Rain 🌧️',
    67: 'Heavy Rain 🌧️',
    71: 'Light Snow 🌨️',
    73: 'Snow 🌨️',
    75: 'Heavy Snow 🌨️',
    77: 'Snow Grains 🌨️',
    80: 'Light Showers 🌧️',
    81: 'Showers 🌧️',
    82: 'Heavy Showers 🌧️',
    85: 'Light Snow Showers 🌨️',
    86: 'Heavy Snow Showers 🌨️',
    95: 'Thunderstorm ⛈️',
    96: 'Thunderstorm with Light Hail ⛈️',
    99: 'Thunderstorm with Heavy Hail ⛈️'
}


#Get weather data using the Open-Meteo URL specified in the YAML file
def get_weather(url):
    #Return a json dictionary containing the weather data
    api_result = requests.get(url)
    return api_result.json()

#Construct weather embed to send, takes the weather json produced in get_weather() above
def weather_embed(weather, colour):
    #Some variables for local time stuffs
    morning_or_not = [0, 12] #Times for 'morning', 'afternoon'. 'Evening' is determined by the 'is_day' attribute in the weather
    current_time = dt.datetime.strptime(weather['current_weather']['time'], '%Y-%m-%dT%H:%M')  + dt.timedelta(minutes=dt.datetime.now().minute) #Datetime object for current time
    wcode = weather['current_weather']['weathercode']

    #Match the greeting to correspond to the time of day
    match np.searchsorted(morning_or_not, current_time.hour, side='right'):
        case 1: #Morning
            greeting = 'Good morning, Sensei! Here is today\'s weather forecast!'
        case 2: #Afternoon or Evening
            if weather['current_weather']['is_day'] == 1:
                greeting = 'Good afternoon, Sensei! Here is today\'s weather forecast!'
            else:
                greeting = 'Good evening, Sensei! Here is today\'s weather forecast!'
    
    #Change the 'sunny' weathers to 'clear' weather
    if (wcode < 10) and (weather['current_weather']['is_day'] == 0): 
        wcode = wcode + 10

    #Current weather to put in the big text at the top of the embed
    current_weather = 'Current weather: ' + str(weather['current_weather']['temperature']) + '°C, ' + code[wcode]

    #Construct the embed with the current weather conditions
    embed = ds.Embed(title=current_weather,
        description=greeting,
        color=colour
    )
    #Add the high and low
    embed.add_field(name='🡹 High 🡹', value=str(weather['daily']['temperature_2m_max'][0])+'°C', inline=False)
    embed.add_field(name='🡻 Low 🡻', value=str(weather['daily']['temperature_2m_min'][0])+'°C', inline=False)

    #Footer containing the time this was sent, based off of the location where the weather is being pulled from
    embed.set_footer(text=dt.datetime.strftime(current_time, '%Y/%m/%d %H:%M ') + weather['timezone_abbreviation'])

    #Return the fully constructed weather embed
    return embed