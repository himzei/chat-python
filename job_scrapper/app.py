from flask import Flask, render_template, request
from scrapper import search_incruit 

app = Flask(__name__) 

@app.route('/')
def home():
    return render_template("home.html")

@app.route("/search")
def search(): 

    keyword = request.args.get("keyword")
    jobs = search_incruit(keyword, 1)
    return render_template("search.html", keyword = keyword, jobs = jobs)

if __name__ == "__main__":
    app.run()
