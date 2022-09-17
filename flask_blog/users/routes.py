from flask_blog import db, bcrypt
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, Blueprint, redirect, url_for, flash, request

from flask_blog.models import User, Post
from flask_blog.users.forms import RegistrationForm, LoginForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm
from flask_blog.users.utils import save_picture
from flask_blog.users.utils import send_reset_email

users = Blueprint('users', __name__)


@users.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('posts.all_posts'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, form.remember.data)

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('posts.all_posts'))
            # return redirect(url_for('main.home'))
        else:
            flash('Войти не удалось. Пожалуйста, проверьте электронную почту и пароль', 'внимание')

    return render_template('login.html', title='Login', form=form)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(username=form.username.data, email=form.email.data, password=hash)

        db.session.add(user)
        db.session.commit()

        flash('Ваша учетная запись успешно создана! Теперь вы можете войти в систему', 'success')

        return redirect(url_for('users.login'))

    return render_template('register.html', title='Register', form=form)


@users.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    posts = []

    form = UpdateProfileForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()

        flash('Ваш аккаунт был обновлен!', 'success')

        return redirect(url_for('users.profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        page = request.args.get('page', 1, type=int)
        user = User.query.filter_by(username=form.username.data).first_or_404()
        # posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    return render_template('profile.html', title='Profile',
                           image_file=image_file, form=form, posts=posts)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    return render_template('all_posts.html', posts=posts, user=user)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('posts.all_posts'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('На почту отправлено письмо с инструкциями (проверьте папку спам).', 'info')

        return redirect(url_for('users.login'))

    return render_template('reset_password.html', title='Сброс пароля', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('posts.all_posts'))

    user = User.verify_reset_token(token)

    if user is None:
        flash('Токен просрочен или недействителен.', 'warning')
        return redirect(url_for('users.reset_password'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        flash('Пароль установлен, можете войти на сайт.', 'success')

        return redirect(url_for('users.login'))

    return render_template('reset_token.html', title='Сброс пароля', form=form)