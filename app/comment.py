import functools

from app.models import *
from flask import session, g,render_template
from app.constants import *
def do_index_class(index):
    """自定义过滤器，过滤点击排序html的class"""
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    else:
        return ""
def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 获取到当前登录用户的id
        user_id = session.get("user_id")
        # 通过id获取用户信息
        user = None
        if user_id:
            from app.models import User
            user = User.query.get(user_id)

        g.user = user
        return f(*args, **kwargs)

    return wrapper
def user_is_login(f):
    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        user = g.user
        if not user:
            return  render_template("news/404.html"),404
        return f(*args,**kwargs)
    return wrapper
class DATA():

    @property
    def categories(self):
        try:
          data= Category.query.all()
        except Exception:
            return  None
        else:
            return data
    @property
    def news_dict(self):
        try:
          data= News.query.filter_by(status=0).order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
        except Exception:
            return  None
        else:
            return data


