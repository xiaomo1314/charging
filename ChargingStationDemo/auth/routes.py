from datetime import date

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from . import auth_bp
from .forms import LoginForm, RegisterForm
from models import User
from extensions import db
from tools import generate_uid


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(uid=form.uid.data).first()
        if user and user.check_password(form.password.data):  # 判断是否是123456
            login_user(user)
            return redirect(url_for('charging.stations'))
        flash('用户名或密码错误')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    generated_uid = generate_uid()
    if form.validate_on_submit():
        # 再次生成，避免并发时产生重复
        final_uid = generate_uid()
        user = User(
            username=form.username.data,
            uid = final_uid,
            uage = form.uage.data,
            regtime=date.today())
        db.session.add(user)
        db.session.commit()
        flash('注册成功！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, uid = generated_uid, reg_date=date.today())


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
