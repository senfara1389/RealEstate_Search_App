import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

with open("data.json", "r") as file:
    data = json.load(file)

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:password@localhost:3306/realestate_database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Advert(db.Model):
    advert_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    residence_type = db.Column(db.String(45), nullable=False)
    transaction_type = db.Column(db.String(45), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    size = db.Column(db.Float(), nullable=False)
    room_count = db.Column(db.Float(), nullable=False)
    parking = db.Column(db.Boolean(), nullable=False)
    heating_type = db.Column(db.String(45), nullable=False)
    bathroom_count = db.Column(db.Float(), nullable=True)
    land = db.Column(db.String(45), nullable=True)
    level = db.Column(db.String(45), nullable=True)
    building_year = db.Column(db.Integer(), nullable=True)
    registered = db.Column(db.Boolean(), nullable=True)
    additional_info = db.Column(db.String(255), nullable=True)

    def __init__(self, residence_type, transaction_type, location, size, room_count, parking, heating_type, bathroom_count=None, land=None, level=None, building_year=None, registered=None, additional_info=None):
        self.residence_type = residence_type
        self.transaction_type = transaction_type
        self.location = location
        self.size = size
        self.room_count = room_count
        self.parking = parking
        self.heating_type = heating_type
        self.bathroom_count = bathroom_count
        self.land = land
        self.level = level
        self.building_year = building_year
        self.registered = registered
        self.additional_info = additional_info


# Traversing through all JSON objects and creating an entry for database
id_list = data.keys()
for estate_id in id_list:
    str_id = str(estate_id)
    ad = data[str_id]
    a = Advert(ad["residence_type"], ad["transaction_type"], ad["location"], ad["size"], ad["room_count"], ad["parking"], ad["heating_type"], ad["bathroom_count"], ad["land"], ad["level"], ad["building_year"], ad["registered"], ad["additional_info"])
    db.session.add(a)
    db.session.commit()
