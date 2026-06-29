import urllib.request
import json
import urllib.parse

API = "76a116fc28c0b3fec7a8a37ed1c96c93"

city = input("City name:")

parameters = {
    'q': city,
    'appid': API,
    'units' : 'metric'
}

print(f"Fetching weather data for {city.capitalize()}...")

encoded_parameters = urllib.parse.urlencode(parameters)
base_url = "https://api.openweathermap.org/data/2.5/weather"
encoded_url = f"{base_url}?{encoded_parameters}"


with urllib.request.urlopen(encoded_url) as response:
    data = response.read().decode('utf-8')

weather = json.loads(data)  

print(f"Temprature: {round(weather['main']['temp'])}°C")
print(f"Humidity: {weather['main']['humidity']}%")
print(f"Pressure: {weather['main']['pressure']} hPa")
print(f"Feels like: {round(weather['main']['feels_like'])}°C")
print(f"Max Temprature: {round(weather['main']['temp_max'])}°C")
print(f"Min Temprature: {round(weather['main']['temp_min'])}°C")
print(f"Sea level: {weather['main']['sea_level']}m")