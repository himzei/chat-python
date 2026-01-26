import csv 

with open("jobs.csv", "w", newline="", encoding="cp949") as file:
    writer = csv.writer(file)

    writer.writerow(["회사이름", "공고제목", "회사위치", "자세히보기"])
    for job in jobs: 
        writer.writerow([job["회사이름"], job["공고제목"], job["회사위치"], job["자세히보기"]])


