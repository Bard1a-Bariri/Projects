import urllib.request
import json
import urllib.parse

API = "76a116fc28c0b3fec7a8a37ed1c96c93"

city = Ottawa, ON

parameters = {
    'q':'City Name'
    'appid': API
    'units' : 'metric'
}

print(f"Fetching weather data for {city}...")

encoded_parameters = urllib.parse.encode(parameters)
base_url = "https://openweathermap.org"
encoded_url = f"{base_url}"?{encoded_parameters}"


with urllib.request.urlopen(encoded_url) as response
    data = response.read.decode('utf-8')

weather = json.loads(data)  

print(weather['main']['humidity'])
print(weather['main']['temp'])
print(weather['main']['feels_like'])
print(weather['main']['pressure'])
