import requests

#Get weather data using the Weatherstack API
#Weatherstack API key and location in the YAML file
def get_weather(url):
    #Return a json dictionary containing the weather data
    api_result = requests.get(url)
    return api_result.json()