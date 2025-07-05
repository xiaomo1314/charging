from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager
from auth import auth_bp
from charging import charging_bp
from flask_login import current_user


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(charging_bp)

    # 根路径路由：判断是否登录，跳转对应页面
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            # 已登录，跳转充电桩列表页面
            return redirect(url_for('charging.stations'))
        else:
            # 未登录，跳转登录页面，假设登录路由为 auth.login
            return redirect(url_for('auth.login'))

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
