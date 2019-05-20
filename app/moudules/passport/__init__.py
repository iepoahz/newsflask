from flask import Blueprint
passport = Blueprint("passport", __name__)
from app.moudules.passport import views