# import os
# from dotenv import load_dotenv
#
# # 加载环境变量（如果没有.env文件，这行可以注释掉，不影响）
# # load_dotenv()
#
#
# class Config:
#     # 数据库配置
#     DB_HOST = os.getenv("DB_HOST", "localhost")  # 从系统环境变量读取，默认localhost
#     DB_USER = os.getenv("DB_USER", "root")       # 默认root
#     DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")  # 默认123456
#     DB_NAME = os.getenv("DB_NAME", "chargingdb")      # 默认chargingdb
#
#     # DeepSeek API配置（修正重点）
#     DEEPSEEK_API_KEY = "key"  # 直接赋值（仅本地测试用）
#     DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
#     DEEPSEEK_MODEL = "deepseek-chat"
#
#     # Flask配置
#     SECRET_KEY = os.getenv("SECRET_KEY", "dev_key_for_test")
#     DEBUG = os.getenv("DEBUG", "True") == "True"



import os
import mysql.connector
from mysql.connector import Error
import pytest
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    # 数据库配置
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
    DB_NAME = os.getenv("DB_NAME", "chargingdb")

    # DeepSeek API配置
    DEEPSEEK_API_KEY = "sk-bc80d95b5fe84116860aaeb046745347"  # 仅本地测试用
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL = "deepseek-chat"

    # Flask配置
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_key_for_test")
    DEBUG = os.getenv("DEBUG", "True") == "True"

