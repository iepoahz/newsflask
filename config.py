import logging
from redis import StrictRedis
import os
class Config(object):
    #项目配置
    #secret-key设置
    SECRET_KEY = "f0f07fbbb1344e4d92bf37ba546c4647"

    #连接配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:zp19961102.@127.0.0.1:3306/info"
    #动态追踪
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 在请求结束时候，如果指定此配置为 True ，那么 SQLAlchemy 会自动执行一次 db.session.commit()操作
    SQLALCHEMY_COMMIT_ON_TEARDOWN =True
    #设置打印sql语句
    # SQLALCHEMY_ECHO = True
    #redis配置
    REDIS_HOST="127.0.0.1"
    REDIS_PORT=6397
    #session保存配置
    SESSION_TYPE="redis"
    # 开启session签名
    SESSION_USE_SIGNER=True
    # 指定 Session 保存的 redis
    SESSION_REDIS=StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    # 设置需要过期
    SESSION_PERMANENT = False
    # 设置过期时间
    PERMANENT_SESSION_LIFETIME=86400*7
    #设置日志等级
    LOG_LEVEL = logging.DEBUG
    #设置json可以返回中文
    JSON_AS_ASCII= False

class DevelopmentConfig(Config):
    #开发环境
    DEBUG = True
class ProductionConfig(Config):
    #生产环境
    DEBUG = True
    LOG_LEVEL = logging.WARNING
config = {
    "development":DevelopmentConfig,
    "production":ProductionConfig,
}