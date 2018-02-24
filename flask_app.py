from collections import OrderedDict
from flask import Flask, jsonify, render_template, request, session
from json import dumps, load
from os.path import abspath, dirname, join
from sqlalchemy import exc as sql_exception
from sys import dont_write_bytecode, path
from werkzeug.utils import secure_filename
from xlrd import open_workbook
from xlrd.biffh import XLRDError

dont_write_bytecode = True
path_app = dirname(abspath(__file__))
if path_app not in path:
    path.append(path_app)

from algorithms.pytsp import pyTSP
from database import db, create_database
from models import City


def configure_database(app):
    create_database()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()
    db.init_app(app)


def import_cities():
    with open(join(path_app, 'data', 'cities.json')) as data:
        for city_dict in load(data):
            if int(city_dict['population']) < 900000:
                continue
            city = City(**city_dict)
            db.session.add(city)
        try:
            db.session.commit()
        except sql_exception.IntegrityError:
            db.session.rollback()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'key'
    configure_database(app)
    import_cities()
    tsp = pyTSP()
    return app, tsp


app, tsp = create_app()


def allowed_file(name, allowed_extensions):
    allowed_syntax = '.' in name
    allowed_extension = name.rsplit('.', 1)[1].lower() in allowed_extensions
    return allowed_syntax and allowed_extension


@app.route('/', methods=['GET', 'POST'])
def index():
    session['best'] = float('inf')
    session['crossover'], session['mutation'] = 'OC', 'Swap'
    view = request.form['view'] if 'view' in request.form else '2D'
    cities = {
        city.id: OrderedDict([
            (property, getattr(city, property))
            for property in City.properties
            ])
        for city in City.query.all()
        }
    return render_template(
        'index.html',
        view=view,
        cities=cities
        )


@app.route('/<algorithm>', methods=['POST'])
def algorithm(algorithm):
    session['best'] = float('inf')
    return jsonify(*getattr(tsp, algorithm)())


if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        threaded = True
        )
