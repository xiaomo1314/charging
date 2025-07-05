from flask import Flask
from app.config import Config

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(Config)

# 导入路由（避免循环导入）
from app import routes