import uuid
from db import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    cep = db.Column(db.String(10))
    logradouro = db.Column(db.String(255))
    bairro = db.Column(db.String(255))
    localidade = db.Column(db.String(255))
    cidade = db.Column(db.String(255))
    number = db.Column(db.String(20))
