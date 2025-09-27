#!/usr/bin/env python3

from flask import Flask, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, User, Recipe

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev"

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


# ---------- Signup ----------
class Signup(Resource):
    def post(self):
        data = request.json
        try:
            user = User(
                username=data["username"],
                image_url=data.get("image_url"),
                bio=data.get("bio")
            )
            user.password_hash = data["password"]
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return user.to_dict(), 201
        except:
            return {"error": "422 Unprocessable Entity"}, 422


# ---------- Check Session ----------
class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401
        user = User.query.get(user_id)
        return user.to_dict(), 200


# ---------- Login ----------
class Login(Resource):
    def post(self):
        data = request.json
        user = User.query.filter_by(username=data.get("username")).first()
        if user and user.authenticate(data.get("password")):
            session["user_id"] = user.id
            return user.to_dict(), 200
        return {"error": "Unauthorized"}, 401


# ---------- Logout ----------
class Logout(Resource):
    def delete(self):
        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401
        session.pop("user_id")
        return {}, 204


# ---------- Recipes ----------
class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401
        recipes = Recipe.query.all()
        return [r.to_dict() for r in recipes], 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401
        data = request.json
        try:
            recipe = Recipe(
                title=data["title"],
                instructions=data["instructions"],
                minutes_to_complete=data["minutes_to_complete"],
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except:
            return {"error": "422 Unprocessable Entity"}, 422


# ---------- API Routes ----------
api.add_resource(Signup, "/signup")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(RecipeIndex, "/recipes")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
