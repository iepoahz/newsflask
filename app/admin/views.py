from app.admin import admin
from flask import redirect,render_template,session,flash,url_for
@admin.route("/")
def index():
    return render_template("admin/index.html")

@admin.route("/login/")
def login():
    return render_template("admin/login.html")
@admin.route("/news/edit/")
def news_edit():
    return render_template("admin/news_edit.html")
@admin.route("/news/edit/detail/")
def news_edit_detail():
    return render_template("admin/news_edit_detail.html")
@admin.route("news/review/")
def news_review():
    return render_template("admin/news_review.html")
@admin.route("/news/review/detail/")
def news_review_detail():
    return render_template("admin/news_review_detail.html")
@admin.route("/news/type/")
def news_type():
    return render_template()
@admin.route("/user/count/")
@admin.route("/user/list/")
