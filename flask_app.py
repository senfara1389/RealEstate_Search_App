import json
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

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


@app.route('/')
def index():
    data = None
    return render_template("index.html", data=data)


@app.route('/read/<int:page_num>', methods=['GET', 'POST'])
def read(page_num):
    data = Advert.query.paginate(per_page=5, page=page_num)
    return render_template("index.html", data=data)


@app.route('/create', methods=['POST'])
def create():
    residence_type = request.form['residence_type']
    transaction_type = request.form['transaction_type']
    location = request.form['location']
    size = request.form['size']
    room_count = request.form['room_count']
    parking = request.form['parking']
    if parking == "True":
        parking = True
    elif parking == "False":
        parking = False
    heating_type = request.form['heating_type']
    bathroom_count = request.form['bathroom_count']
    building_year = request.form['building_year']
    registered = request.form['registered']
    if registered == "True":
        registered = True
    elif registered == "False":
        registered = False
    if residence_type == "kuca":
        level = None
        land = request.form['land']
    elif residence_type == "stan":
        land = None
        level = str(request.form['this_level']) + " / " + str(request.form['all_levels'])
    additional_info = request.form['additional_info']

    a = Advert(residence_type, transaction_type, location, size, room_count, parking, heating_type, bathroom_count, land, level, building_year, registered, additional_info)
    db.session.add(a)
    db.session.commit()

    return redirect(url_for("index", data="Uspešno dodata nekretnina u bazu"))


if __name__ == "__main__":
    app.run(debug=True)

