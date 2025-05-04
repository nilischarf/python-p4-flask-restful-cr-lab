#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant  # Use Plant model

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

# Root route
class Home(Resource):
    def get(self):
        return make_response({
            "message": "Welcome to the Plant RESTful API"
        }, 200)

api.add_resource(Home, '/')


# /plants (GET all & POST new)
class Plants(Resource):
    def get(self):
        plants = Plant.query.all()
        return make_response(
            [plant.to_dict() for plant in plants],
            200
        )

    def post(self):
        data = request.get_json()

        # Check for required fields
        if not all(field in data for field in ['name', 'image', 'price']):
            return make_response({'error': 'Missing required fields'}, 400)

        try:
            new_plant = Plant(
                name=data['name'],
                image=data['image'],
                price=data['price']
            )
            db.session.add(new_plant)
            db.session.commit()

            return make_response(new_plant.to_dict(), 201)
        except Exception as e:
            db.session.rollback()
            return make_response({'error': str(e)}, 400)

api.add_resource(Plants, '/plants')


# /plants/<int:id> (GET one)
class PlantByID(Resource):
    def get(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            return make_response({'error': 'Plant not found'}, 404)

        return make_response(plant.to_dict(), 200)

api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)