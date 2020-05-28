import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager



db = SQLAlchemy()

def create_app(test_config=None):
    from .models import User
    app = Flask(__name__, instance_relative_config=True, template_folder='./templates')
    app.config['SECRET_KEY'] = 'E5Bw4g!I}Kb:;o='
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    db.init_app(app)
    db.app = app

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Админская часть
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    # Главная страница
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
