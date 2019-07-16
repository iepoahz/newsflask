from flask_script import Manager
from flask import render_template
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db, models
from flask_wtf.csrf import generate_csrf
# manage.py是程序启动的入口，只关心启动的相关参数以及内容

# 通过指定的配置名字创建对应配置的app
# 指定环境
app = create_app('development')

manager = Manager(app=app)
# 将 app 与 db 关联
Migrate(app, db)
# 将迁移命令添加到manager中
manager.add_command('db', MigrateCommand)

@app.errorhandler(404)
def error(error):
    return render_template("news/404.html"),404
@app.after_request
def after_request(response):
    # 调用函数生成 csrf_token
    csrf_token = generate_csrf()
    # 通过 cookie 将值传给前端
    response.set_cookie("csrf_token", csrf_token)
    return response
if __name__ == '__main__':
    manager.run()

















# from flask_script import Manager
# # from flask_migrate import Migrate,MigrateCommand
# # from app import create_app,db,models
# # app = create_app("development")
# # manager = Manager(app)
# # Migrate(app,db)
# # manager.add_command("db",MigrateCommand)
# # if __name__ == '__main__':
# #     manager.run()