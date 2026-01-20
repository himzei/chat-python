import requests
import json 

api_key = "532b43b6e382f182b0c43695a34f48ae"
city_name = "구미" 
lat = 36.2101
lon = 128.3544

url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"

response = requests.get(url) 

data = json.loads(response.text)

print(f"{city_name}의 날씨 : {data['weather'][0]['description']}")
print(f"현재 온도 : {data['main']['temp']}")
print(f"체감 온도 : {data['main']['feels_like']}")