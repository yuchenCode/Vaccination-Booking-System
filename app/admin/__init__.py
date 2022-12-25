from flask import Blueprint
# create blueprint
admin = Blueprint('admin', __name__)
from . import views