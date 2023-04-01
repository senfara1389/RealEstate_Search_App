import json
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:password@localhost:3306/realestate_database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '13€$'

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
    message = request.args.get('message')
    if message is None:
        print("pocetak")
    else:
        print(message)
    return render_template("index.html", data=None, message=message)


@app.route('/read/', methods=['GET', 'POST'], defaults={'page_num': 1})
@app.route('/read/<int:page_num>', methods=['GET', 'POST'])
def read(page_num):
    new_search = request.args.get("option")
    if new_search == "True" and request.form['id_show'] != "":
        id_show = request.form['id_show']
        data = Advert.query.filter(Advert.advert_id == id_show)
        data = data.paginate(per_page=1, page=page_num)
    else:
        if new_search == "True":
            if 'house' in session:
                session.pop('house', None)
            if 'parking' in session:
                session.pop('parking', None)
            if 'min_squares' in session:
                session.pop('min_squares', None)
            if 'max_squares' in session:
                session.pop('max_squares', None)

            if 'house' in request.form:
                session['house'] = request.form['house']
            if 'parking' in request.form:
                session['parking'] = request.form['parking']
                if session['parking'] == "True":
                    session['parking'] = 1
                elif session['parking'] == "False":
                    session['parking'] = 0
            session['min_squares'] = request.form['min_squares']
            session['max_squares'] = request.form['max_squares']

            if session['min_squares'] > session['max_squares']:
                return render_template("index.html", data=None, message=
                "Vrednost minimalne kvadrature mora biti manja od vrednosti maksimalne")

        data = Advert.query

        if 'house' in session and session['house'] != "":
            data = data.filter(Advert.residence_type == session['house'])

        if 'parking' in session and session['parking'] != "":
            data = data.filter(Advert.parking == session['parking'])

        if 'min_squares' in session and session['max_squares'] != "":
            data = data.filter(Advert.size < session['max_squares'])

        if 'max_squares' in session and session['min_squares'] != "":
            data = data.filter(Advert.size > session['min_squares'])

        data = data.paginate(per_page=5, page=page_num)

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
    if bathroom_count == '':
        bathroom_count = None
    building_year = request.form['building_year']
    if building_year == '':
        building_year = None
    registered = request.form['registered']
    level = None
    land = None
    if registered == "True":
        registered = 1
    elif registered == "False":
        registered = 0
    if residence_type == "kuća":
        level = None
        land = request.form['land']
    elif residence_type == "stan":
        land = None
        level = str(request.form['this_level']) + " / " + str(request.form['all_levels'])
    additional_info = request.form['additional_info']
    additional_info = additional_info.strip()
    if additional_info == '':
        additional_info = None

    a = Advert(residence_type, transaction_type, location, size, room_count, parking, heating_type, bathroom_count, land, level, building_year, registered, additional_info)
    db.session.add(a)

    failed = False
    try:
        db.session.commit()
    except Exception as e:
        print("An error has occured: " + str(e))
        db.rollback()
        db.flush()
        failed = True

    if failed is True:
        return redirect(url_for("index", message="Došlo je do greške pri upisu"))

    return redirect(url_for("index", message="Uspešno dodata nekretnina u bazu"))


@app.route('/update', methods=['POST'])
def update():
    estate_id = request.form['estate_id']
    entry = Advert.query.get(estate_id)

    residence_type = request.form['residence_type']
    if residence_type != "None":
        entry.residence_type = residence_type

    transaction_type = request.form['transaction_type']
    if transaction_type != "None":
        entry.transaction_type = transaction_type

    location = request.form['location']
    if location != "":
        entry.location = location

    size = request.form['size']
    if size != "":
        entry.size = size

    room_count = request.form['room_count']
    if room_count != "":
        entry.room_count = room_count

    parking = request.form['parking']
    if parking != "None":
        if parking == "True":
            parking = True
        elif parking == "False":
            parking = False
        entry.parking = parking

    heating_type = request.form['heating_type']
    if heating_type != "":
        entry.heating_type = heating_type

    bathroom_count = request.form['bathroom_count']
    if bathroom_count != "":
        entry.bathroom_count = bathroom_count

    building_year = request.form['building_year']
    if building_year != "":
        entry.building_year = building_year

    registered = request.form['registered']
    if registered != "None":
        if registered == "True":
            registered = 1
        elif registered == "False":
            registered = 0
        entry.registered = registered

    if residence_type == "kuća":
        land = request.form['land']
        if land != "":
            entry.land = land

    elif residence_type == "stan":
        this_level = request.form['this_level']
        all_levels = request.form['all_levels']
        if this_level != "" and all_levels != "":
            entry.level = str(this_level) + " / " + str(all_levels)

    additional_info = request.form['additional_info']
    additional_info = additional_info.strip()
    if additional_info != '':
        entry.additional_info = additional_info

    db.session.commit()
    return redirect(url_for("index", message="Uspešno izmenjena nekretnina u bazi"))

if __name__ == "__main__":
    app.run(debug=True)

