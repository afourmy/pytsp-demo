from threading import Lock
from flask import Flask, jsonify, render_template, request, session
from json import dumps, load
from os.path import abspath, dirname, join
from sqlalchemy import exc as sql_exception
from sys import dont_write_bytecode, path

dont_write_bytecode = True
path_app = dirname(abspath(__file__))
if path_app not in path:
    path.append(path_app)

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
            if int(city_dict['population']) < 800000:
                continue
            city = City(**city_dict)
            db.session.add(city)
        try:
            db.session.commit()
        except sql_exception.IntegrityError:
            db.session.rollback()

def create_app(config='config'):
    app = Flask(__name__)
    app.config.from_object('config')
    configure_database(app)
    from algorithms.pytsp import pyTSP
    tsp = pyTSP()
    import_cities()
    return app, tsp


app, tsp = create_app()


@app.route('/', methods=['GET', 'POST'])
def index():
    session['best'] = float('inf')
    session['crossover'], session['mutation'] = 'OC', 'Swap'
    view = request.form['view'] if 'view' in request.form else '2D'
    cities = {
        city.id: {
            property: getattr(city, property)
            for property in City.properties
            }
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
    return jsonify(*getattr(tsp, algorithm)(), False)


if __name__ == '__main__':
    app.run()
