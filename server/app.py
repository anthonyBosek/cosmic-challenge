#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def home():
    return ""


class Scientists(Resource):
    def get(self):
        scientists = [s.to_dict(rules=("-missions",)) for s in Scientist.query]
        return scientists, 200

    def post(self):
        try:
            req_data = request.get_json()
            scientist = Scientist(**req_data)
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(rules=("-missions",)), 201
        except ValueError:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400


api.add_resource(Scientists, "/scientists")


class ScientistById(Resource):
    def get(self, id):
        if scientist := db.session.get(Scientist, id):
            return scientist.to_dict(), 200
        return {"error": "Scientist not found"}, 404

    def patch(self, id):
        try:
            req_data = request.get_json()
            if scientist := db.session.get(Scientist, id):
                for key, val in req_data.items():
                    setattr(scientist, key, val)
                db.session.commit()
                return scientist.to_dict(rules=("-missions",)), 202
            return {"error": "Scientist not found"}, 404
        except:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400

    def delete(self, id):
        try:
            if scientist := db.session.get(Scientist, id):
                db.session.delete(scientist)
                db.session.commit()
                return {}, 204
            return {"error": "Scientist not found"}, 404
        except:
            db.session.rollback()
            return {"error": f"Could not delete Scientist with id {id}"}, 404


api.add_resource(ScientistById, "/scientists/<int:id>")


class Planets(Resource):
    def get(self):
        planets = [p.to_dict(rules=("-missions",)) for p in Planet.query]
        return planets, 200


api.add_resource(Planets, "/planets")


class Missions(Resource):
    def post(self):
        try:
            req_data = request.get_json()
            mission = Mission(**req_data)
            db.session.add(mission)
            db.session.commit()
            return mission.to_dict(), 201
        except ValueError:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400


api.add_resource(Missions, "/missions")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
