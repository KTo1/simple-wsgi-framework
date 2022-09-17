from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from flask_blog.config import Config
from flask_mail import Mail


db = SQLAlchemy()
lm = LoginManager()
bcrypt = Bcrypt()
mail = Mail()


def create_app():
    print(__name__)
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    lm.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    from flask_blog.main.routes import main
    from flask_blog.users.routes import users
    from flask_blog.posts.routes import posts
    from flask_blog.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(errors)

    return app
