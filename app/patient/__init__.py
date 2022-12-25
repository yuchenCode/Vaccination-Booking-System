from flask import Blueprint
# create blueprint
patient = Blueprint('patient', __name__)
from . import views


