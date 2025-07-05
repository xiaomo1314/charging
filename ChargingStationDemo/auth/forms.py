from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, Length, NumberRange


class LoginForm(FlaskForm):
    uid = StringField('用户ID', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 32)])
    password = PasswordField('密码', validators=[DataRequired()])
    uage = IntegerField('年龄', validators=[DataRequired(), NumberRange(min=18, max=40)])
    submit = SubmitField('注册')
