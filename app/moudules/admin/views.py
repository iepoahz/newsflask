from app.moudules.admin import admin
from flask import render_template


@admin.route("/login/")
def index():
    return render_template("admin/index.html")

@admin.route("/")
def login():
    return render_template("admin/login.html")

# @admin.route("/news/edit/")
# def news_edit():
#     return render_template("admin/news_edit.html")
#
# @admin.route("/news/edit/detail/")
# def news_edit_detail():
#     return render_template("admin/news_edit_detail.html")
#
# @admin.route("news/review/")
# def news_review():
#     return render_template("admin/news_review.html")
#
# @admin.route("/news/review/detail/")
# def news_review_detail():
#     return render_template("admin/news_review_detail.html")
#
# @admin.route("/news/type/")
# def news_type():
#     return render_template("admin/news_type.html")
#
# @admin.route("/user/count/")
# def user_count():
#     return render_template("admin/user_count.html")
#
# @admin.route("/user/list/")
# def user_list():
#     return render_template("admin/user_list.html")
