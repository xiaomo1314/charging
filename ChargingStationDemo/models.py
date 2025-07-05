from datetime import date

from extensions import db, login_manager
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    uid = db.Column(db.String(10), primary_key=True)  # 用户编号（字符串，如 U018）
    username = db.Column(db.String(32), unique=True, nullable=False)  # 用户姓名
    uage = db.Column(db.Integer)  # 用户年龄
    regtime = db.Column(db.Date, default=date.today, nullable=False)  # 注册时间

    def check_password(self, password):
        return password == '123456'  # 简化：所有用户密码都是 123456

    def get_id(self):
        return self.uid  # 不再转为 int，直接返回字符串主键


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)  # 不转 int，直接使用字符串


class Station(db.Model):
    __tablename__ = 'station'

    stationid = db.Column(db.String(10), primary_key=True)  # 充电桩编号（字符串，如 S001）
    facilitytype = db.Column(db.Integer)  # 充电桩类型
    location = db.Column(db.String(128))  # 充电桩位置


class UseInfo(db.Model):
    __tablename__ = 'useinfos'

    uid = db.Column(db.String(10), db.ForeignKey('user.uid'), primary_key=True)  # 用户编号
    stationid = db.Column(db.String(10), db.ForeignKey('station.stationid'), primary_key=True)  # 充电桩编号
    begintime = db.Column(db.DateTime, primary_key=True)  # 充电开始时间
    endtime = db.Column(db.DateTime)  # 充电结束时间
    money = db.Column(db.Float)  # 消费金额
