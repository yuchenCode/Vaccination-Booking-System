from flask import Blueprint
# create blueprint
auth = Blueprint('auth', __name__)
from . import views
