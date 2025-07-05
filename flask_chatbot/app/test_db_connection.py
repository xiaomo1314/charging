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


@pytest.fixture(scope="module")
def db_connection():
    """创建数据库连接的 fixture，供测试用例使用"""
    conn = None
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        assert conn.is_connected(), "数据库连接失败"
        yield conn
    except Error as e:
        pytest.fail(f"数据库连接失败: {str(e)}")
    finally:
        if conn and conn.is_connected():
            conn.close()


def test_connection(db_connection):
    """测试数据库连接是否正常"""
    assert db_connection.is_connected(), "连接已断开"


def test_query_user_table(db_connection):
    """测试查询用户表"""
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT uid, username FROM user LIMIT 5")
    users = cursor.fetchall()
    cursor.close()
    assert len(users) > 0, "用户表无数据或查询失败"
    print("\n用户表前5条数据：")
    for user in users:
        print(f"  {user['uid']}: {user['username']}")


def test_query_march_usage(db_connection):
    """测试查询2023年3月充电记录"""
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT COUNT(*) as total FROM useinfos 
        WHERE begintime >= '2023-03-01 00:00:00' 
          AND begintime < '2023-04-01 00:00:00'
    """)
    result = cursor.fetchone()
    cursor.close()
    assert result is not None, "充电记录查询失败"
    print(f"\n2023年3月充电记录总数：{result['total']}条")


def test_query_station_table(db_connection):
    """测试查询充电站表"""
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT stationid, location FROM station LIMIT 3")
    stations = cursor.fetchall()
    cursor.close()
    assert len(stations) > 0, "充电站表无数据或查询失败"
    print("\n充电站表前3条数据：")
    for station in stations:
        print(f"  {station['stationid']}: {station['location']}")