import requests
from bs4 import BeautifulSoup 
import csv 

def search_incruit(keyword, page=1):
    jobs = []

    for i in range(page):

        page = i * 30 

        response =requests.get(f"https://search.incruit.com/list/search.asp?col=job&kw={keyword}&startno={page}")
        # print(f"https://search.incruit.com/list/search.asp?col=job&kw={keyword}")
        # # print(response.text)

        soup = BeautifulSoup(response.text, "html.parser")

        lis = soup.find_all("li", class_="c_col")

        # print(len(lis)) 

        for li in lis:
            try:
                # 회사 이름 추출
                company = li.find("a", class_="cpname").text.strip()
                
                # cell_mid 안의 cl_top에서 실제 채용 공고 링크를 찾아야 함
                # (첫 번째 cl_top은 회사명 링크만 있고, 실제 공고 링크는 cell_mid 안에 있음)
                cell_mid = li.find("div", class_="cell_mid")
                if cell_mid:
                    cl_top = cell_mid.find("div", class_="cl_top")
                    if cl_top:
                        title_link = cl_top.find("a")
                        if title_link:
                            title = title_link.text.strip()
                            link = title_link.get("href", "")
                        else:
                            title = ""
                            link = ""
                    else:
                        title = ""
                        link = ""
                else:
                    title = ""
                    link = ""
                
                # 위치 정보 추출
                cl_md = li.find("div", class_="cl_md")
                if cl_md:
                    location_spans = cl_md.find_all("span")
                    location = location_spans[0].text.strip() if location_spans else ""
                else:
                    location = ""
                
                # 데이터 딕셔너리 생성 및 추가
                job_data = {
                    "회사이름": company,
                    "공고제목": title, 
                    "회사위치": location,
                    "자세히보기": link
                }
                
                jobs.append(job_data)
            except Exception as e:
                # 에러 발생 시 해당 항목 건너뛰기
                print(f"항목 처리 중 오류 발생: {e}")
                continue

    return jobs 


jobs = search_incruit("파이썬", 10)

with open("jobs.csv", "w", newline="", encoding="cp949") as file:
    writer = csv.writer(file)

    writer.writerow(["회사이름", "공고제목", "회사위치", "자세히보기"])
    for job in jobs: 
        writer.writerow([job["회사이름"], job["공고제목"], job["회사위치"], job["자세히보기"]])











