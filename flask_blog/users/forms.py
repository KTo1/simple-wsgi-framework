from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

from flask_blog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя: ', validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('Почта: ', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль: ', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль: ', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            ValidationError('Это имя уже занято.')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            ValidationError('Эта почта уже занята.')


class LoginForm(FlaskForm):
    email = StringField('Почта: ', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль: ', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')

    submit = SubmitField('Войти')


class UpdateProfileForm(FlaskForm):

    username = StringField('Имя пользователя: ', validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('Почта: ', validators=[DataRequired(), Email()])
    picture = FileField('Обновить фото профиля', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Обновить')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                ValidationError('Это имя уже занято.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                ValidationError('Эта почта уже занята.')


class RequestResetForm(FlaskForm):
    email = StringField('Почта: ', validators=[DataRequired(), Email()])
    submit = SubmitField('Изменить пароль')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            ValidationError('Пользователь с таким email не найден! Вы можете использовать его для регистрации. ')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль: ', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль: ', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Установить')
