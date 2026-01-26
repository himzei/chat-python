import requests
from bs4 import BeautifulSoup 

keyword = "간호사"
response =requests.get(f"https://search.incruit.com/list/search.asp?col=job&kw={keyword}")
# print(f"https://search.incruit.com/list/search.asp?col=job&kw={keyword}")
# # print(response.text)

soup = BeautifulSoup(response.text, "html.parser")

lis = soup.find_all("li", class_="c_col")

# print(len(lis)) 
for li in lis:
    company = li.find("a", class_="cpname").text
    print(company)