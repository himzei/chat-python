import requests 
from bs4 import BeautifulSoup


def search_incruit(term, page=1): 
    jobs = [] 
    for i in range(page): 
        page = 1 + i 

        response = requests.get(
            f"https://search.incruit.com/list/search.asp?col=job&kw={term}&startno={page}", 
            headers={
                "User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        soup = BeautifulSoup(response.text, "html.parser")

        lis = soup.find_all("li", class_="c_col")
        
        for li in lis: 
            company = li.find("a", class_="cpname").text
            title = li.find("div", class_="cl_top").text 
            link = li.find("div", class_="cl_top").find("a").get("href")
            location = li.find("div", class_="cl_md").find_all("span")[2].text

            job_data = {
                "title": title, 
                "company": company, 
                "link": link, 
                "location": location
            }

            jobs.append(job_data)
        
    return jobs

def search_jobkorea(term, page=1):
    jobs = [] 
    for i in range(page): 
        
        page = 30 * i 

        response = requests.get(
            f"https://www.jobkorea.co.kr/Search/?stext={term}&tabType=recruit&Page_No={page}"
            
        )
        soup = BeautifulSoup(response.text, "html.parser")
        lis = soup.find_all("article", class_="list-item")

        for li in lis: 
            try: 
                company = li.find("div", class_="list-section-corp").find("a").text
                title = li.find("div", class_="information-title").find("a").text
                location = li.find_all("li", class_="chip-information-item")[3].text
                link = li.find("div", class_="information-title").find("a").get("href")

                job_data = {
                    "title": title.strip(), 
                    "company": company.strip(), 
                    "link": f"https://www.jobkorea.co.kr{link}",
                    "location": location
                }

                jobs.append(job_data)

            except: 
                pass
        
    return jobs



result = search_incruit("python")
print(result)