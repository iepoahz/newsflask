from flask import Blueprint
news = Blueprint("news",__name__)
import app.moudules.news.views
