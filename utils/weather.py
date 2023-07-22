import requests
import numpy as np
import datetime as dt
import discord as ds

#Weathercodes, 10, 11, 12, and 13 are not real codes, but I want to use them to substitute the sun in the case of night reports
code = {
    0: ['Sunny', '☀️'],
    1: ['Mostly Sunny', '🌤️'],
    2: ['Partly Cloudy', '⛅'],
    3: ['Overcast', '☁️'],
    10: ['Clear', '🌕'],
    11: ['Mostly Clear', '🌙'],
    12: ['Partly Clear', '🌙'],
    13: ['Overcast', '☁️'],
    45: ['Foggy', '🌫️'],
    48: ['Foggy', '❄️'],
    51: ['Light Drizzle', '🌧️'],
    53: ['Drizzle', '🌧️'],
    55: ['Heavy Drizzle', '🌧️'],
    56: ['Light Drizzle', '🌧️'],
    57: ['Heavy Drizzle', '🌧️'],
    61: ['Light Rain', '🌧️'],
    63: ['Rain', '🌧️'],
    65: ['Heavy Rain', '🌧️'],
    66: ['Light Rain', '🌧️'],
    67: ['Heavy Rain', '🌧️'],
    71: ['Light Snow', '🌨️'],
    73: ['Snow', '🌨️'],
    75: ['Heavy Snow', '🌨️'],
    77: ['Snow Grains', '🌨️'],
    80: ['Light Showers', '🌧️'],
    81: ['Showers', '🌧️'],
    82: ['Heavy Showers', '🌧️'],
    85: ['Light Snow Showers', '🌨️'],
    86: ['Heavy Snow Showers', '🌨️'],
    95: ['Thunderstorm', '⛈️'],
    96: ['Thunderstorm with Light Hail', '⛈️'],
    99: ['Thunderstorm with Heavy Hail', '⛈️']
}

#Temperature bars for the 12-hour bar graph function
temp_bars = {
    12: '🟥🟥🟧🟧🟨🟨🟩🟩🟦🟦🟪🟪',
    11: '⬛🟥🟧🟧🟨🟨🟩🟩🟦🟦🟪🟪',
    10: '⬛⬛🟧🟧🟨🟨🟩🟩🟦🟦🟪🟪',
    9: '⬛⬛⬛🟧🟨🟨🟩🟩🟦🟦🟪🟪',
    8: '⬛⬛⬛⬛🟨🟨🟩🟩🟦🟦🟪🟪',
    7: '⬛⬛⬛⬛⬛🟨🟩🟩🟦🟦🟪🟪',
    6: '⬛⬛⬛⬛⬛⬛🟩🟩🟦🟦🟪🟪',
    5: '⬛⬛⬛⬛⬛⬛⬛🟩🟦🟦🟪🟪',
    4: '⬛⬛⬛⬛⬛⬛⬛⬛🟦🟦🟪🟪',
    3: '⬛⬛⬛⬛⬛⬛⬛⬛⬛🟦🟪🟪',
    2: '⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟪🟪',
    1: '⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟪'
}

#Clocks for the 12-hour bar graph
clocks = '🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚'

#Get weather data using the Open-Meteo URL specified in the YAML file
def get_weather(url):
    #Return a json dictionary containing the weather data
    api_result = requests.get(url)
    return api_result.json()

#Return 12 hour temperature forecast as a bar graph, starting from current local time of the location
def current(weather, colour, location):
    #Gather all of the necessary variables from the weather data
    offset = int(weather['current_weather']['time'][-5:-3])  #Get hour offset for the day
    clock_label = clocks[(offset % 12):] + clocks[:(offset % 12)] #Shift clocks to the left to match the hour, use modulo to account for 24h time
    x = np.arange(start=0, stop=12, step=1) + offset #Indices to get hourly data from
    temp = [weather['hourly']['temperature_2m'][i] for i in x] #Temperatures
    wcode = [weather['hourly']['weathercode'][i] for i in x] #Weathercodes
    day = [weather['hourly']['is_day'][i] for i in x] #Day or night?

    #Create 'buckets in order to categorize the temperatures into the 12 bars
    buckets = np.linspace(start=np.min(temp), stop=np.max(temp), num=12)

    #Generate the bar graph. Right now, it is rotated on its side.
    to_rotate = []
    for t in temp[::-1]:
        to_rotate.append(temp_bars[np.searchsorted(buckets, t, side='right')])
    
    #Clever trick to rotate the bar graph 90 degrees clockwise to the correct orientation
    rotated = list(zip(*to_rotate[::-1]))
    
    #Generate the emoji string to represent the forecasted weather conditions
    for i in range(len(wcode)):
        if (wcode[i] < 10) and (day[i] == 0): 
            wcode[i] += 10 #Use moons in the case that it dark outside
    sky = ''.join([code[w][1] for w in wcode])

    #Begin constructing the final string that will be sent by the bot
    final = [str(round(buckets[::-1].tolist()[i], 1)) for i in range(len(buckets))] #Start with the temperatures on the y-axis

    #Clean up the temperature display to show min, mid, and max temperature
    for i in range(len(final)):
        if i in [0, 6, 11]:
            final[i] = '`' + final[i] + '°C`'
        else:
            final[i] = '`      `'

    #Complete the leftmost column to start attaching everything else to
    final.insert(0, '`      `'); final.append('`      `')

    #Append everything to create the complete bar graph
    final[0] += sky + '\n'
    for i in range(len(rotated)):
        final[i+1] += ''.join(rotated[i]) + '\n'
    final[-1] += clock_label

    #Now to put everything into an embed
    current_weather = 'Current weather: ' + str(weather['current_weather']['temperature']) + '°C, ' + code[wcode[0]][0] + ' ' + code[wcode[0]][1] #Title string
    current_time = now(weather['utc_offset_seconds']) #Datetime object for current time
    embed = ds.Embed(title=current_weather,
        description=''.join(final),
        color=colour
    )
    #Add the high/low fields and the time footer
    embed.add_field(name='⬆️ High ⬆️', value=str(weather['daily']['temperature_2m_max'][0]) + '°C', inline=False)
    embed.add_field(name='⬇️ Low ⬇️', value=str(weather['daily']['temperature_2m_min'][0]) + '°C', inline=False)
    embed.set_footer(text=location + '\n' + dt.datetime.strftime(current_time, '%Y/%m/%d %H:%M ') + weather['timezone_abbreviation'])

    #Return the embed
    return time_of_day(current_time.hour, day[0]), embed

#Forecast n days (1-7)
def forecast(weather, n, colour, location):
    #Construct the strings for the days at
    days = ['` ' + weather['daily']['time'][i][-5:].replace('-', '/') + '`' + code[weather['daily']['weathercode'][i]][1] for i in range(n)]
    #High and low temperature
    high = ['`' + str(weather['daily']['temperature_2m_max'][i]).center(6) + '`⬛' for i in range(n)]
    low = ['`' + str(weather['daily']['temperature_2m_min'][i]).center(6) + '`⬛' for i in range(n)]

    day_row = '`    `🗓️' + ''.join(days)
    high_row = '\n`HIGH`⬆️' + ''.join(high)
    low_row = '\n` LOW`⬇️' + ''.join(low)

    current_time = now(weather['utc_offset_seconds']) #For the footer

    embed = ds.Embed(title=str(n) + ' Day Forecast',
        description=day_row + high_row + low_row,
        color=colour
    )
    embed.set_footer(text=location + '\n' + dt.datetime.strftime(current_time, '%Y/%m/%d %H:%M ') + weather['timezone_abbreviation'])

    return embed

#Quick helper to return current time as local time for the selected location
def now(utc_offset):
    return dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(seconds=utc_offset) #Datetime object for current time

#Helper function to determine what to say given the time of day
def time_of_day(hour, is_day):
    match np.searchsorted([0, 12], hour, side='right'):
        case 1: #Morning
            greeting = 'Good morning, Sensei!'
        case 2: #Afternoon or Evening
            if is_day == 1:
                greeting = 'Good afternoon, Sensei!'
            else:
                greeting = 'Good evening, Sensei!'
    
    return greeting