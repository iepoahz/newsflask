from app.news import news
from flask import render_template,redirect,session,flash,url_for
@news.route("/")
def index():
    return render_template("news/index.html")