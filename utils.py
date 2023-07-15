import requests
import wave
import numpy as np

#Get weather data using the Weatherstack API
#Weatherstack API key and location in the YAML file
def get_weather(key, loc):
    #Parameters to pass into the requests.get()
    params = {
        'access_key': key,
        'query': loc
    }

    #Return a json dictionary containing the weather data
    api_result = requests.get('http://api.weatherstack.com/forecast', params)
    return api_result.json()

#Distort the wav file to be sent by the bot
def distort_wav(original, distorted, thresh, temp):
    #Load in the wave reader/writer objects
    atsui = wave.open(original, 'rb')
    yoooo = wave.open(distorted, 'wb')

    #Get number of frames
    frames = atsui.getnframes()

    #Read into bytearray and close the original wav file
    b = bytearray(atsui.readframes(frames))
    atsui.close()

    #Do funny stuff to the file, do crazier stuff depending on how much higher the temperature is compared to the threshold
    amp = 5 * (temp - thresh)
    freq = 200 * (temp - thresh) * np.pi
    noise = amp * np.sin(np.linspace(start=0, stop=freq, num=len(b))) * np.random.choice([-1, 1], size=len(b))

    for i in range(len(b)):
        b[i] = max(min(b[i] + int(noise[i]), 255), 0)
    
    yoooo.setparams(atsui.getparams())
    yoooo.writeframes(data=b)
    yoooo.close()