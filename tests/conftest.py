import os
import pytest
import importlib

from db import db


@pytest.fixture(scope="session")
def app():
    os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

    import main
    importlib.reload(main)

    flask_app = main.create_app()
    flask_app.config["TESTING"] = True

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()