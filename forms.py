from logging import error
from re import L
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, PasswordField
from wtforms.validators import Email, DataRequired, Length


class UserForm(FlaskForm):
    nick = StringField("Ник:", validators=[DataRequired(), Length(4, 16)])
    password = PasswordField("Пароль:", validators=[DataRequired(), Length(5, 50)])
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    check_nick = StringField("Ник:", validators=[Length(4, 16)])
    check_pass = StringField("Пароль:", validators=[Length(5, 50)])
    submit = SubmitField("Войти")


class UpdateForm(FlaskForm):
    upd_nick = StringField("Ник:")
    upd_password = StringField("Пароль:")
    submit = SubmitField("Обновить данные")


class ChatForm(FlaskForm):
    message = TextAreaField("Текст сообщения", validators=[DataRequired()])
    submit = SubmitField("Отправить сообщение")


class MailForm(FlaskForm):
    sender = StringField("Отправитель", validators=[Email()])
    message = TextAreaField("Текст сообщения", validators=[DataRequired()])
    submit = SubmitField("Отправить сообщение")