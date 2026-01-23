import requests
from bs4 import BeautifulSoup 

response =requests.get("https://search.incruit.com/list/search.asp?col=job&kw=%B0%A3%C8%A3%BB%E7")
# print(response.text)

soup = BeautifulSoup(response.text, "html.parser")
print(soup)