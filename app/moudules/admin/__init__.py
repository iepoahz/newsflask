from flask import Blueprint#导入蓝图
admin = Blueprint("admin",__name__)
import app.moudules.admin.views