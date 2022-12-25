from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from config import config, config_name

# create app
app = Flask(__name__)
app.config.from_object(config[config_name])
config[config_name].init_app(app)
bootstrap = Bootstrap()
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# init app
bootstrap.init_app(app)
db.init_app(app)
login_manager.init_app(app)

moment = Moment()
moment.init_app(app)

# register blueprint
from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from .patient import patient as patient_blueprint
app.register_blueprint(patient_blueprint)

from .doctor import doctor as doctor_blueprint
app.register_blueprint(doctor_blueprint)

from .admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint)
