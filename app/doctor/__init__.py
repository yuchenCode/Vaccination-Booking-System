from flask import Blueprint
# create blueprint
doctor = Blueprint('doctor', __name__)
from . import views