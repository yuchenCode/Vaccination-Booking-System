# run this to init db
from app import db
db.drop_all()
db.create_all()
