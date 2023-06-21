#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
from sqlalchemy.exc import IntegrityError
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///camp.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return 'Home'

api = Api(app)
class Activites(Resource):
    def get(self):
        activities = [a.to_dict() for a in Activity.query.all()]
        return make_response(jsonify(activities), 200)
        
api.add_resource(Activites, '/activities')

class Campers(Resource):
    def get(self):
        campers = [c.to_dict() for c in Camper.query.all()]
        return make_response(jsonify(campers), 200)
    def post(self):
        try:
            data = request.get_json()
            camper = Camper(**data)
            db.session.add(camper)
            db.session.commit()
            return make_response(jsonify(camper.to_dict()), 201)
        except (Exception, IntegrityError) as e:
            return make_response(jsonify({"error": str(e)}), 400)
api.add_resource(Campers, '/campers')

class CamperByID(Resource):
    def get(self, id):
        camper = db.session.get(Camper, id)
        if camper:
            return make_response(jsonify(camper.to_dict(only=('id', 'name', 'age', 'signups.activity'))), 200)
        else:
            return make_response(jsonify({'error': 'Camper not found'}), 404)
    def patch(self, id):
        try:
            camper = db.session.get(Camper, id)
            if not camper:
                return make_response(jsonify({'error': '404: Camper not found'}), 404)
            data = request.get_json()
            for key, value in data.items():
                setattr(camper, key, value)
            db.session.commit()
            return make_response(jsonify(camper.to_dict(only=('id', 'name', 'age', 'signups.activity'))), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 400)
    def delete(self, id):
        try:
            camper = db.session.get(Camper, id)
            db.session.delete(camper)
            db.session.commit()
            return make_response(jsonify({}), 204)
        except (Exception, IntegrityError) as e:
            return make_response(jsonify({'error': '404: Camper not found'}), 404)
api.add_resource(CamperByID, '/campers/<int:id>')
            
    

if __name__ == '__main__':
    app.run(port=5555, debug=True)
