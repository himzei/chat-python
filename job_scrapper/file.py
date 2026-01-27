import csv 
import os

def save_to_csv(jobs):
    # 현재 스크립트의 디렉토리를 기준으로 절대 경로 생성
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs.csv")
    with open(csv_path, "w", newline="", encoding="cp949") as file:
        writer = csv.writer(file)

        writer.writerow(["회사이름", "공고제목", "회사위치", "자세히보기"])
        for job in jobs: 
            writer.writerow([job["회사이름"], job["공고제목"], job["회사위치"], job["자세히보기"]])


