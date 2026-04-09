from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
import os
import requests

from db import db
from models import User


def serialize_user(user):
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "cep": user.cep,
        "logradouro": user.logradouro,
        "bairro": user.bairro,
        "localidade": user.localidade,
        "cidade": user.cidade,
        "number": user.number,
    }


def create_app():
    app = Flask(__name__)
    CORS(app)

    postgres_user = os.environ.get("POSTGRES_USER", "appuser")
    postgres_password = os.environ.get("POSTGRES_PASSWORD", "apppass")
    postgres_url = os.environ.get("POSTGRES_URL", "localhost")

    db_uri = f"postgresql://{postgres_user}:{postgres_password}@{postgres_url}:5432/users"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        db_uri,
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    @app.route("/users", methods=["POST"])
    def create_user():
        data = request.get_json(silent=True) or {}

        required_fields = ["name", "email", "cep", "number"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing field: {field}"}), 400

        cep = str(data["cep"]).strip().replace("-", "").replace(".", "").replace(" ", "")
        if len(cep) != 8 or not cep.isdigit():
            return jsonify({"error": "CEP inválido"}), 400

        try:
            via_cep_response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        except requests.RequestException:
            return jsonify({"error": "Erro ao consultar CEP"}), 500

        if via_cep_response.status_code != 200:
            return jsonify({"error": "Erro ao consultar CEP"}), 500

        cep_data = via_cep_response.json()

        if cep_data.get("erro"):
            return jsonify({"error": "CEP inválido"}), 400

        user = User(
            name=data["name"],
            email=data["email"],
            cep=cep_data.get("cep", cep),
            logradouro=cep_data.get("logradouro", ""),
            bairro=cep_data.get("bairro", ""),
            localidade=cep_data.get("localidade", ""),
            cidade=cep_data.get("localidade", ""),
            number=data["number"],
        )

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Erro ao salvar usuário"}), 400

        return jsonify(serialize_user(user)), 201

    @app.route("/users/<uuid:user_id>", methods=["GET"])
    def get_user(user_id):
        user = User.query.get_or_404(user_id)
        return jsonify(serialize_user(user)), 200

    @app.route("/users/<string:email>/email", methods=["GET"])
    def get_user_by_email(email):
        user = User.query.filter_by(email=email).first_or_404()
        return jsonify(serialize_user(user)), 200

    @app.route("/users/<uuid:user_id>", methods=["DELETE"])
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return "", 204

    @app.route("/users", methods=["GET"])
    def list_users():
        users = User.query.all()
        return jsonify([serialize_user(user) for user in users]), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)