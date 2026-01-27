from flask import Flask, render_template, request, send_file
from scrapper import search_incruit
from file import save_to_csv
import os

app = Flask(__name__) 
page_num = 2

@app.route('/')
def home():
    return render_template("home.html")

@app.route("/search")
def search(): 
    keyword = request.args.get("keyword")
    jobs = search_incruit(keyword, page_num)
    return render_template("search.html", keyword = keyword, jobs = jobs)

@app.route("/download")
def download(): 
    keyword = request.args.get("keyword")
    jobs = search_incruit(keyword, page_num)
    save_to_csv(jobs)

    # 현재 스크립트의 디렉토리를 기준으로 절대 경로 생성
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs.csv")
    return send_file(csv_path, as_attachment=True)

if __name__ == "__main__":
    app.run()
