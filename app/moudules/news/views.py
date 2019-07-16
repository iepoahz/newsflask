import os
import uuid

from app.moudules.news import news
from flask import render_template, redirect, url_for, session, jsonify, request, make_response,g
from app.models import *
from app.comment import *
from app.response_code import RET

#todo 首页
@news.route("/")
@user_login_data
def index():
    data=DATA()
    data={
        "user":g.user,
        "categories":data.categories,
        "news_dict":data.news_dict
    }
    return render_template("news/index.html",data=data)
#todo 新闻列表
@news.route("/news_list")
def news_list():
    if request.method=="GET":
        page = request.args.get("page")

        cid = request.args.get("cid")
        if not all([page, cid]):
            return jsonify(errmsg="新闻页面加载失败")
        try:
            page = int(page)
            cid = int(cid)
        except Exception:
            return jsonify(errmsg = "参数错误")
        li=[News.status==0]
        if cid != 1:
            li.append(News.category_id==cid)
        try:
            data= News.query.filter(*li).order_by(News.create_time.desc()).paginate(page=page, per_page=HOME_PAGE_MAX_NEWS,error_out=False)
        except Exception:
            return jsonify(errmsg="获取新闻失败")
        items = data.items
        news_li=[]
        for new in items:
            news_li.append(new.to_basic_dict())
        page = data.page
        pages = data.pages
        data = {
            # "cid":cid,
            "cur_page" :page,
            "total_page":pages,
            "news_dict_list":news_li,
                }
        return jsonify(errno=RET.OK,data=data)
#todo 新闻详情页

@news.route("/<int:news_id>")
@user_login_data
def detail(news_id):
    data = DATA()
    user=g.user
    try:
        news=News.query.filter(News.status==0,News.id==news_id).first()
        news_dict = news.to_dict()
    except Exception:
        return jsonify(errmsg ="没有此新闻")
    try:
        news_comment = Comment.query.filter_by(news_id=news_id).order_by(Comment.create_time.desc())
    except Exception:
        return jsonify(errmsg="此新闻评论查询失败")


    comment_like_ids=[]
    is_collected = False
    is_followed = False
    if user:
        # 判断是否点赞
        try:
            #新闻评论的id列表
            commentid = [comment.id for comment in news_comment]

            #用户点赞的新闻评论
            comment_like_ = CommentLike.query.filter(CommentLike.comment_id.in_(commentid),CommentLike.user_id==user.id).all()

            # 用户点赞的新闻评论的id列表
            comment_like_ids = [comment_like_id.comment_id for comment_like_id in comment_like_]

        except Exception:
            return jsonify(errmsg="此用户点赞查询失败")

        # 判断是否收藏

        try:
            is_collect = user.collection_news.all()
            is_follow = user.followed
        except Exception:
            return jsonify(errmsg="获取失败")
        if news in is_collect:
            is_collected =True
        if news.user in is_follow:
            is_followed = True
    news_comment_li = []
    for comment in news_comment:
        commentdict = comment.to_dict()
        commentdict["is_like"] = False
        if comment.id in comment_like_ids:
            commentdict["is_like"] = True
        news_comment_li.append(commentdict)
    data = {
        "user": user.to_dict() if user else None,
        "categories": data.categories,
        "news_dict": data.news_dict,
        "news": news_dict,
        "is_collected": is_collected,
        "is_followed": is_followed,
        "comments": news_comment_li
    }
    # 更新点击量
    try:

        news.clicks += 1

        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify("点击量更新失败")
    return render_template("news/detail.html", data=data)
#todo 新闻收藏
@news.route("/news_collect", methods=['POST'])
@user_login_data
def news_collect():
    if not g.user:
        return jsonify(errno= RET.SESSIONERR,errmsg="请登录您的账号")
    user =g.user
    news_id = int(request.json.get("news_id"))
    action = request.json.get("action")
    if not all([news_id, action]):
        return jsonify(errmsg="参数错误")
    try:
        news=News.query.get(news_id)
    except Exception:
        return jsonify(errmsg="没有此新闻")
    if action == "cancel_collect":
        try:
            user.collection_news.remove(news)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify(errmsg="取消收藏失败")
    if action == "collect":
        try:
            user.collection_news.append(news)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify(errmsg="收藏失败")
    return jsonify(errno=RET.OK)
#todo 添加评论
@news.route('/news/news_comment', methods=["POST","GET"])
@user_login_data
def add_news_comment():

    if not g.user:
        return jsonify(errno=RET.SESSIONERR,errmsg = "未登录")
    news_id = request.json.get("news_id")
    comment = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    if not all([news_id,comment]):
        return jsonify(errmsg="参数不全")
    try:
        News.query.filter_by(id=news_id).first()
    except Exception:
        return jsonify(errmsg ="此新闻已删除")
    try:
        news_comment = Comment()
        if parent_id:
            news_comment.parent_id = int(parent_id)
        news_comment.news_id = int(news_id)
        news_comment.user_id = int(g.user.id)
        news_comment.content = comment
        db.session.add(news_comment)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(errmsg="评论失败")
    try:
        news_comment = Comment.query.filter_by(news_id=news_id).order_by(Comment.create_time.desc()).first()
    except Exception:
        return jsonify(errmsg="此新闻评论查询失败")
    data = news_comment.to_dict()
    return jsonify(errno = RET.OK,errmsg = "评论成功",user_id=g.user.id,data=data)
#todo 评论删除
@news.route("/news_comment/del",methods = ["POST"])
@user_login_data
def del_news_comment():
    del_comment_id = request.json.get("del_comment_id")
    if not del_comment_id:
        return jsonify(errmsg="参数错误")
    try:
        del_comment = Comment.query.filter_by(id = del_comment_id).first()
        comment_like_user =  CommentLike.query.filter_by(comment_id = del_comment_id).all()
        for userid in comment_like_user:
            db.session.delete(userid)
        db.session.delete(del_comment)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(errmsg = "删除失败")
    return jsonify(errno = RET.OK,errmsg = "删除成功")
#todo 点赞
@news.route('/news/comment_like', methods=["POST"])
@user_login_data
def comment_like():
    user = g.user
    if not user:
        return  jsonify(errno = RET.SESSIONERR,errmsg="未登录")
    comment_id = int(request.json.get("comment_id"))
    action  = request.json.get("action")
    if not all([action,comment_id]):
        return jsonify(errnsg="参数不足")

    commentlike = CommentLike()
    commentlikecount = Comment.query.filter_by(id = comment_id).first()
    if action=="add":
        try:
            commentlike.user_id=user.id
            commentlike.comment_id =comment_id
            commentlikecount.like_count += 1
            db.session.add(commentlike)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify(errmsg="点赞失败/点赞数更新失败")

    if action == "remove":
        try:
            comment = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                               CommentLike.user_id == user.id).first()
        except Exception:
            return jsonify(errmsg="评论查询失败")
        try:
            db.session.delete(comment)
            commentlikecount.like_count -= 1
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify(errmsg = "取消点赞失败/点赞数更新失败（减）")

    return jsonify(errno = RET.OK)
#todo 关注作者
@news.route("/news/followed_user",methods =["POST"])
@user_login_data
def news_follows():
    """关注或者取消关注用户"""

    # 获取自己登录信息
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="未登录")

    # 获取参数
    user_id = request.json.get("user_id")
    action = request.json.get("action")

    # 判断参数
    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("follow", "unfollow"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 获取要被关注的用户
    try:
        other = User.query.get(user_id)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not other:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    if other.id == user.id:
        return jsonify(errno=RET.PARAMERR, errmsg="请勿关注自己")

    # 根据要执行的操作去修改对应的数据
    if action == "follow":
        if other not in user.followed:
            # 当前用户的关注列表添加一个值
            user.followed.append(other)
        else:
            return jsonify(errno=RET.DATAEXIST, errmsg="当前用户已被关注")
    else:
        # 取消关注
        if other in user.followed:
            user.followed.remove(other)
        else:
            return jsonify(errno=RET.DATAEXIST, errmsg="当前用户未被关注")

    return jsonify(errno=RET.OK, errmsg="操作成功")



#todo 个人中心
@news.route("/user/info")
@user_login_data
@user_is_login
def user_info():
    data = {
        "user":g.user
    }
    return render_template("news/user.html",data = data)
#todo 基本详情页
@news.route("/user/base_info",methods=["GET","POST"])
@user_login_data
@user_is_login
def user_base_info():
    user = g.user
    if request.method == "GET":
        data = {"user":user.to_dict()}
        return render_template("news/user_base_info.html",data = data)
    elif request.method =="POST":
        signature = request.json.get("signature")
        nick_name = request.json.get("nick_name")
        gender = request.json.get("gender")
        print(gender)
        if not all([signature,nick_name,gender]):
            return jsonify(errmsg = "参数不够")
        try :
            user.nick_name = nick_name
            user.signature = signature
            if gender == "woman":
                user.gender = "WOMAN"
            user.gender = "MAN"
            user_news = user.news_list.all()
            # print(user_news)
            if user_news:
                for news in user_news:
                    news.source = nick_name
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify(errmsg="保存失败")
        return jsonify(errno=RET.OK)
#换文件名
def change_filename(filename):
    fileinfo = os.path.splitext(filename)  # 分离包含路径的文件名与包含点号的扩展名
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex + fileinfo[-1])
    return filename
#todo 头像详情页
@news.route("/user/pic_info",methods=["GET","POST"])
@user_login_data
@user_is_login
def user_pic_info():
    user = g.user
    if request.method == "GET":
        data = {"user": user.to_dict()}
        return render_template("news/user_pic_info.html",data = data)
    if request.method == "POST":
        avatar = request.files.get("avatar")
        try:
            # 文件保存路径操作
            file_save_path = UP_DIR # 文件上传保存路径
            if not os.path.exists(file_save_path):
                os.makedirs(file_save_path)  # 如果文件保存路径不存在，则创建一个多级目录
                import stat
                os.chmod(file_save_path, stat.S_IRWXU)  # 授予可读写权限
            # 对上传的文件进行重命名
            url = change_filename(avatar.filename)
            # 保存文件，需要给文件的保存路径+文件名
            avatar.save(file_save_path + url)
            avatar_url = "../../static/avatar_media/"+url
            print(file_save_path+url)
        except Exception:
            return jsonify(errmsg="上传失败")
        try:
            user_avatar_url = user.avatar_url
            if user_avatar_url:
                urlli = user_avatar_url.split("/")
                if os.path.exists(file_save_path+urlli[-1]):
                    os.remove(file_save_path+urlli[-1])
        except Exception:
            return jsonify(errmsg="原头像删除失败")

        try:
            user.avatar_url = avatar_url
            db.session.commit()
        except Exception:

            db.session.rollback()
            return jsonify(errmsg ="保存失败")
        data = {
                "avatar_url" :avatar_url
            }
        return jsonify(errno = RET.OK,data = data)
#todo 密码详情页
@news.route("/user/pass_info",methods=["GET","POST"])
@user_login_data
@user_is_login
def user_pass_info():
    user = g.user
    if request.method == "GET":
        data = {"user": user.to_dict()}
        return render_template("news/user_pass_info.html",data = data)
    if request.method == "POST":
        old_password = request.json.get("old_password")
        new_password = request.json.get("new_password")
        print(old_password,new_password)
        if not all([new_password,old_password]):
            return jsonify(errmsg = "参数不全")
        if not user.check_password(old_password):
            return jsonify(errmsg="当前密码错误")
        try:
            user.password=new_password
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify(errmsg ="修改失败")
        return jsonify(errno = RET.OK)
#todo 关注详情页
@news.route("/user/follow",methods=["GET","POST"])
@user_login_data
@user_is_login
def user_follow():
    user = g.user
    if request.method == "GET":
        page = request.args.get("p")
        if page:
            page = int(page)
        else:
            page = 1
        follows = user.followed.paginate(page=page, per_page=HOME_PAGE_MAX_NEWS, error_out=False)
        newsli = []
        for follow in follows.items:
            newsli.append(follow.to_dict())

        data = {"users": newsli,
                "current_page": follows.page,
                "total_page": follows.pages}
        return render_template("news/user_follow.html",data = data)
    if request.method == "POST":
        """关注或者取消关注用户"""

        # 获取参数
        user_id = request.json.get("user_id")
        action = request.json.get("action")

        # 判断参数
        if not all([user_id, action]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

        if action not in ("follow", "unfollow"):
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

        # 获取要被关注的用户
        try:
            other = User.query.get(user_id)
        except Exception as e:
            return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

        if not other:
            return jsonify(errno=RET.NODATA, errmsg="未查询到数据")


        # 根据要执行的操作去修改对应的数据
        if action == "unfollow":
            # 取消关注
            if other in user.followed:
                user.followed.remove(other)
            else:
                return jsonify(errno=RET.DATAEXIST, errmsg="当前用户已取消关注")

        return jsonify(errno=RET.OK, errmsg="操作成功")
#todo 收藏详情页
@news.route("/user/collection")
@user_login_data
@user_is_login
def user_collection():
    user = g.user
    page = request.args.get("p")
    if page:
        page = int(page)
    else:
        page=1
    try:
        collections = user.collection_news.paginate(page=page,per_page=HOME_PAGE_MAX_NEWS,error_out=False)
    except Exception:
        return render_template("news/404.html"),404
    newsli = []
    for news in collections.items:
        newsli.append(news.to_review_dict())

    data = {"collections": newsli,
            "current_page":collections.page,
            "total_page":collections.pages}
    return render_template("news/user_collection.html",data = data)


#todo 新闻详情页
@news.route("/user/news_list")
@user_login_data
@user_is_login
def user_news_list():
    user = g.user
    page = request.args.get("p")
    if page:
        page = int(page)
    else:
        page = 1
    try:
        selfnews = user.news_list.order_by(News.create_time.desc()).paginate(page=page, per_page=HOME_PAGE_MAX_NEWS, error_out=False)
    except Exception:
        return render_template("news/404.html"),404
    newsli = []
    for news in selfnews.items:
        newsli.append(news.to_review_dict())

    data = {"news_list": newsli,
            "current_page": selfnews.page,
            "total_page": selfnews.pages}
    return render_template("news/user_news_list.html", data=data)

#todo 新闻发布页
@news.route("/user/news_release",methods=["GET","POST"])
@user_login_data
@user_is_login
def user_news_release():
    categoris = Category.query.all()
    user = g.user
    if request.method == "GET":
        categoriesli = []
        for category in categoris:
            category = category.to_dict()
            categoriesli.append(category)
        data = {"categories":categoriesli }
        return render_template("news/user_news_release.html",data = data)
    if request.method == "POST":
        title = request.form.get("title")
        category_id = int(request.form.get("category_id"))
        digest = request.form.get("digest")
        index_image = request.files.get("index_image")
        content = request.form.get("content")
        source = user.nick_name
        print(title,category_id,digest,index_image,content,source)

        if not all([title,category_id,digest,index_image,content]):
            return jsonify(errmsg="参数不全")
        createnews = News()
        try:
            try:
                # 文件保存路径操作
                file_save_path = NEWS_DIR  # 文件上传保存路径
                if not os.path.exists(file_save_path):
                    os.makedirs(file_save_path)  # 如果文件保存路径不存在，则创建一个多级目录
                    import stat
                    os.chmod(file_save_path, stat.S_IRWXU)  # 授予可读写权限
                # 对上传的文件进行重命名
                url = change_filename(index_image.filename)
                # 保存文件，需要给文件的保存路径+文件名
                index_image.save(file_save_path + url)
                index_image_url = "../../static/news_media/" + url
                print(file_save_path + url)
            except Exception:
                return jsonify(errmsg="上传图片失败")
            createnews.title = title
            createnews.category_id = category_id
            createnews.digest = digest
            createnews.content = content
            createnews.source = source
            createnews.index_image_url = index_image_url
            createnews.user_id = user.id
            createnews.status = 0
            db.session.add(createnews)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify(errmsg = "发布失败")
        return jsonify(errno = RET.OK)
#todo 其他用户界面
@news.route("/other")
@user_login_data
def other():
    myself = g.user
    page = request.args.get("p")
    user_id = request.args.get("id")
    if user_id:
        user_id = int(user_id)
    if page:
        page = int(page)
    else:
        page = 1
    is_followed =False
    try:
        is_follow = myself.followed
        user = User.query.get(user_id)
        newsli= user.news_list.filter(News.status==0).order_by(News.create_time.desc()).paginate(page=page, per_page=HOME_PAGE_MAX_NEWS,
                                                                         error_out=False)
    except Exception:
        return  render_template("news/404.html"),404
    if user in is_follow:
        is_followed = True
    news_li = newsli.items
    newslist = []
    for news in news_li:
        newslist.append(news.to_dict())
    data={
        "user":myself,
        "otheruser":user,
        "news_list":newslist,
        "current_page": newsli.page,
        "total_page": newsli.pages,
        "is_followed":is_followed,
    }
    return render_template("news/other.html",data= data)































# @news.route("/detail_list")
# def detail_list():
#     title = request.args.get("title")
#     pic = request.args.get("pic")
#     detail = request.args.get("detail")
#     print(title, pic, detail)
#     if not all([detail, title, pic]):
#         return jsonify(errmsg="获取新闻失败1")
#     if not (title and pic):
#         return jsonify(errmsg="参数错误1")
#     try:
#         data = News.query.filter_by(digest=detail).first()
#         data = data.to_basic_dict()
#     except Exception:
#         return jsonify(errmsg="获取新闻失败2")
#     elif pic and detail:
#         return jsonify(errmsg="参数错误2")
#     try:
#         data = News.query.filter_by(title=title).first()
#         data = data.to_basic_dict()
#         print(data)
#     except Exception:
#         return jsonify(errmsg="获取新闻失败3")
#     if detail and title:
#         return jsonify(errmsg="参数错误3")
#     pic = pic.spilt("?")
#     try:
#         data = News.query.filter_by(index_image_url=pic[0]).first()
#         data = data.to_basic_dict()
#     except Exception:
#         return jsonify(errmsg="获取新闻失败4")
#     return  jsonify(data=data)



#     title = request.args.get("title")
#     pic = request.args.get("pic")
#     detail = request.args.get("detail")
#     if not all([title,pic,detail]):
#         return jsonify(errmsg="出错了")
#     if title == "" and pic=="" and detail=="":
#         return jsonify(errmsg="获取新闻失败")
#     if title == "" and pic=="":
#         try:
#             data = News.query.filter_by(digest=detail).first
#         except Exception:
#             return jsonify(errmsg="获取新闻失败")
#     if pic =="" and detail =="":
#         try:
#             data = News.query.filter_by(title=title).first
#         except Exception:
#             return jsonify(errmsg="获取新闻失败")
#     if title=="" and  detail =="":
#         pic=pic.spilt("?")
#         try:
#             data = News.query.filter_by(index_image_url=pic[0]).first
#         except Exception:
#             return jsonify(errmsg="获取新闻失败")
#     try:
#         data=data.to_basic_dict()
#     except Exception:
#         return jsonify(errmsg="获取新闻失败")
#     return jsonify(data =data)
# @news.route("/detail/")
# def detail ():
#     return render_template("news/detail.html")
# @news.route("/other/")
# def other ():
#     return render_template("news/other.html")
# @news.route("/user/")
# def user ():
#     return render_template("news/user.html")
# @news.route("/user/base/info/")
# def use_base_info ():
#     return render_template("news/user_base_info.html")
# @news.route("/user/collection/")
# def user_collection ():
#     return render_template("news/user_collection.html")
# @news.route("/user/follow/")
# def user_follow ():
#     return render_template("news/user_follow.html")
# @news.route("/user/news/list/")
# def user_news_list ():
#     return render_template("news/user_news_list.html")
# @news.route("/user/news/release/")
# def user_news_release ():
#     return render_template("news/user_news_release.html")
# @news.route("/user/pass/info/")
# def user_pass_info ():
#     return render_template("news/user_pass_info.html")
# @news.route("/user/pic/info/")
# def user_pic_info ():
#     return render_template("news/user_pic_info.html")

