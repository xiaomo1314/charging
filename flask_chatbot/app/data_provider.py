import mysql.connector
from mysql.connector import Error
from app import app


class DataProvider:
    """获取充电桩分析数据（集成Spark查询功能）"""

    def __init__(self):
        self.db_config = {
            "host": app.config["DB_HOST"],
            "user": app.config["DB_USER"],
            "password": app.config["DB_PASSWORD"],
            "database": app.config["DB_NAME"],
            "charset": "utf8mb4"
        }

    def get_connection(self):
        """创建数据库连接"""
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            app.logger.error(f"数据库连接失败: {str(e)}")
            return None

    def get_analysis_context(self):
        """获取充电桩分析核心数据（集成新增业务需求）"""
        conn = self.get_connection()
        if not conn:
            return "当前无法获取分析数据，请稍后重试"

        try:
            context = []
            cursor = conn.cursor(dictionary=True)

            # --------------------------
            # 基础分析数据（保留原有）
            # --------------------------
            # 1. 总营业额（2023年3月）
            cursor.execute("""
                SELECT SUM(money) as total_revenue 
                FROM useinfos 
                WHERE begintime >= '2023-03-01 00:00:00' AND begintime < '2023-04-01 00:00:00'
            """)
            revenue = cursor.fetchone()["total_revenue"] or 0
            context.append(f"2023年3月总营业额：{revenue:.2f}元")

            # 2. 充电桩总使用次数
            cursor.execute("""
                SELECT COUNT(*) as total_usage 
                FROM useinfos 
                WHERE begintime >= '2023-03-01 00:00:00' AND begintime < '2023-04-01 00:00:00'
            """)
            usage_count = cursor.fetchone()["total_usage"] or 0
            context.append(f"2023年3月充电桩总使用次数：{usage_count}次")

            # 3. 高峰时段（Top3）
            cursor.execute("""
                SELECT HOUR(begintime) as hour, COUNT(*) as count 
                FROM useinfos 
                WHERE begintime >= '2023-03-01 00:00:00' AND begintime < '2023-04-01 00:00:00'
                GROUP BY hour ORDER BY count DESC LIMIT 3
            """)
            peak_hours = cursor.fetchall()
            peak_str = ", ".join([f"{h['hour']}点（{h['count']}次）" for h in peak_hours])
            context.append(f"3月高峰充电时段（Top3）：{peak_str}")

            # 4. 各城区充电桩使用次数 - 修复usage关键字问题
            cursor.execute("""
                SELECT s.location, COUNT(f.uid) as `usage` 
                FROM useinfos f JOIN station s ON f.stationid = s.stationid
                WHERE f.begintime >= '2023-03-01 00:00:00' AND f.begintime < '2023-04-01 00:00:00'
                GROUP BY s.location
            """)
            location_usage = cursor.fetchall()
            loc_str = ", ".join([f"{l['location']}：{l['usage']}次" for l in location_usage])
            context.append(f"各城区使用次数：{loc_str}")

            # --------------------------
            # 新增用户消费统计（Spark查询集成）
            # --------------------------
            context.append("\n===== 用户消费统计 =====")

            # 1. 平均消费超过40元的用户（取前5名）
            cursor.execute("""
                SELECT
                  u.username,
                  AVG(f.money) as avg_money
                FROM useinfos f
                JOIN user u ON f.uid = u.uid
                GROUP BY u.uid, u.username
                HAVING avg_money > 40
                ORDER BY avg_money DESC
                LIMIT 5
            """)
            high_avg_users = cursor.fetchall()
            if high_avg_users:
                high_avg_str = ", ".join([f"{u['username']}（{u['avg_money']:.2f}元）" for u in high_avg_users])
                context.append(f"平均消费超40元的用户（前5）：{high_avg_str}")
            else:
                context.append("平均消费超40元的用户：无")

            # 2. 充电次数最多的10个用户
            cursor.execute("""
                SELECT
                  u.username,
                  COUNT(f.uid) as usage_count
                FROM useinfos f
                JOIN user u ON f.uid = u.uid
                WHERE f.begintime >= '2023-03-01 00:00:00' AND f.begintime < '2023-04-01 00:00:00'
                GROUP BY u.uid, u.username
                ORDER BY usage_count DESC
                LIMIT 10
            """)
            top_usage_users = cursor.fetchall()
            top_usage_str = ", ".join([f"{u['username']}（{u['usage_count']}次）" for u in top_usage_users])
            context.append(f"充电次数Top10用户：{top_usage_str}")

            # 3. 消费金额最多的10个用户
            cursor.execute("""
                SELECT
                  u.username,
                  SUM(f.money) as total_money
                FROM useinfos f
                JOIN user u ON f.uid = u.uid
                WHERE f.begintime >= '2023-03-01 00:00:00' AND f.begintime < '2023-04-01 00:00:00'
                GROUP BY u.uid, u.username
                ORDER BY total_money DESC
                LIMIT 10
            """)
            top_revenue_users = cursor.fetchall()
            top_revenue_str = ", ".join([f"{u['username']}（{u['total_money']:.2f}元）" for u in top_revenue_users])
            context.append(f"消费金额Top10用户：{top_revenue_str}")

            # --------------------------
            # 新增：按首次充电时间统计每日新增用户
            # --------------------------
            context.append("\n===== 首次充电用户统计 =====")
            cursor.execute("""
                SELECT
                  DATE(first_usage_time) as date,
                  COUNT(*) as new_users
                FROM (
                  SELECT uid, MIN(begintime) as first_usage_time
                  FROM useinfos
                  WHERE begintime >= '2023-03-01 00:00:00' AND begintime < '2023-04-01 00:00:00'
                  GROUP BY uid
                ) as first_usage
                GROUP BY DATE(first_usage_time)
                ORDER BY date
                LIMIT 5  # 取前5天数据，避免过长
            """)
            daily_new_users = cursor.fetchall()
            daily_new_str = ", ".join([f"{d['date']}新增{d['new_users']}人" for d in daily_new_users])
            context.append(f"3月每日新增首充用户（前5天）：{daily_new_str}")

            return "\n".join(context)

        except Error as e:
            app.logger.error(f"数据查询失败: {str(e)}")
            return "分析数据获取失败，请稍后重试"
        finally:
            conn.close()