# from io import BytesIO
import re
import random
from datetime import datetime
from flask import request, current_app, abort, make_response, jsonify, session
from app.models import User
from app.moudules.passport import passport
from app.utils.util.captcha import captcha
from app import redis_store, constants, db
from app.response_code import RET


@passport.route('/image_code')
def get_image_code():
    if request.method=="GET":
        image_code_id = request.args.get("code_id")
        print(image_code_id)
        if not image_code_id:
            current_app.logger.debug("未获取参数")
            abort(403)
        name, text, image = captcha.generate_captcha()
        print("图形验证码", text)
        try:
            redis_store.set("image_code"+image_code_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)
            current_app.logger.info(text)
        except Exception as e :
            current_app.logger.error("保存图片验证码信息失败  %s" % e)
            return jsonify(errno =RET.DBERR,ermmsg="保存图片验证码信息失败")
        resp = make_response(image)
        resp.headers["ContentType"] ="image/png"
        return resp
@passport.route('/sms_code', methods=["POST"])
def send_sms_code():
    if request.method=="POST":
        mobile = request.json.get("mobile")
        print(type(mobile))
        image_code =request.json.get("image_code")
        image_code_id = request.json.get("image_code_id")
        if not all([mobile,image_code,image_code_id]):
            return jsonify(errno=RET.PARAMERR,ermmsg="参数错误")
        if not re.match("^1[3-9]\d{9}$",mobile):
            return jsonify(errno=RET.DATAERR,errmsg="请输入有效手机号")
        try:
            mobile_num = User.query.filter_by(mobile=mobile).count()
        except Exception as e:
            current_app.logger.error("查询手机号失败 %s" % e)
            return jsonify(errno =RET.DBERR,ermmsg="查询手机号失败")
        if mobile_num == 1:
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已注册")
        try:
            image = redis_store.get("image_code"+image_code_id)
        except Exception as e:
            current_app.logger.error("查询图片验证码失败 %s" % e)
            return jsonify(errno=RET.DBERR, ermmsg="查询图片验证码失败")
        if not image:
            return jsonify(errno=RET.DBERR,ermmsg="图片验证码失效")
        if image_code.upper()!=image.upper():
            return jsonify(errno=RET.IMAGEERR,errmsg="图片验证码错误")
        data ="%06d" % random.randint(0,999999)
        # print(type(data))
        # ccp = CCP()
        # ccp_num = ccp.send_template_sms(mobile, [data, constants.SMS_CODE_REDIS_EXPIRES], 1)
        # if ccp_num == -1:
        #     return jsonify(errno=RET.THIRDERR,errmsg="短信发送失败")
        current_app.logger.debug(data)
        try:
            redis_store.set("sms" + mobile, data, constants.SMS_CODE_REDIS_EXPIRES)
        except Exception as e:
            current_app.logger.error("保存短信验证码信息失败  %s" % e)
            return jsonify(errno=RET.DBERR, errmsg="保存短信验证码信息失败")
        return jsonify(errno=RET.OK,errmsg="发送成功")

@passport.route("/register", methods=["POST", "GET"])
def register():
    if request.method=="POST":
        mobile=request.json.get("mobile")
        smscode=request.json.get("sms_code")
        password=request.json.get("password")
        password1=request.json.get("password1")
        if not all([mobile,smscode,password,password1]):
           return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
        try:
           sms_code = redis_store.get("sms" + mobile)
        except Exception as e:
           current_app.logger.error("查询手机验证码失败 %s" % e)
           return jsonify(errno=RET.DBERR, ermmsg="查询手机验证码失败")
        if not sms_code:
           return jsonify(errno=RET.DBERR, ermmsg="手机验证码失效")
        if sms_code != smscode:
           return jsonify(errno=RET.DATAERR,errmsg="手机验证码错误")
        if len(password) < 6 :
           return jsonify(errno=RET.DATAERR,errmsg="密码少于六位")
        if len(password) > 32:
           return jsonify(errno=RET.DATAERR,errmsg="密码大于32位")
        try:
           password=password.encode("ascii")
        except Exception as e:
           return jsonify(errno=RET.DATAERR,errmsg="密码中有英文，数字，符号外的特殊字符")
        else:
           password=password.decode("utf-8")
        if password != password1:
            return jsonify(errno=RET.DATAERR,errmsg="两次密码不一致")
        user=User()
        user.nick_name = mobile
        user.mobile = mobile
        user.password = password
        try:
           db.session.add(user)
        except Exception:
           db.session.rollback()
           return jsonify(errno=RET.DATAERR,errmsg="账号存储异常")
        else:
           db.session.commit()

        return jsonify(errno=RET.OK)
@passport.route("/login", methods=["POST"])

def login():
    if request.method=="POST":
        mobile = request.json.get("mobile")
        password = request.json.get("password")
        image_code = request.json.get("image_code")
        image_code_id = request.json.get("image_code_id")
        if not all([mobile,password,image_code,image_code_id]):
            return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
        if not re.match("^1[3-9]\d{9}$",mobile):
            return jsonify(errno=RET.DATAERR,errmsg="请输入有效手机号")
        try:
            mobile_num = User.query.filter_by(mobile=mobile).first()
        except Exception as e:
            current_app.logger.error("查询手机号失败 %s" % e)
            return jsonify(errno =RET.DBERR,ermmsg="查询手机号失败")
        if not mobile_num:
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号未注册")
        try:
            image = redis_store.get("image_code"+image_code_id)
        except Exception as e:
            current_app.logger.error("查询图片验证码失败 %s" % e)
            return jsonify(errno=RET.DBERR, ermmsg="查询图片验证码失败")
        if not image:
            return jsonify(errno=RET.DBERR,ermmsg="图片验证码无数据")
        if image_code.upper()!=image.upper():
            return jsonify(errno=RET.IMAGEERR,errmsg="图片验证码错误")
        if not mobile_num.check_password(password):
            return jsonify(errno=RET.DATAERR, errmsg="请输入正确密码")
        mobile_num.last_login = datetime.now()
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify(errno=RET.DATAERR,errmsg="登录时间记录异常")
        # session["user_mobile"] = mobile_num.mobile
        session["user_id"]= mobile_num.id
        return jsonify(errno=RET.OK)
@passport.route("/logout",methods=["POST"])
def logout():
    session.pop("user_id")
    return jsonify(errno=RET.OK)