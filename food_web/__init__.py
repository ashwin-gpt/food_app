from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # ✅ SINGLE INSTANCE

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'food_app'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    db.init_app(app)  # ✅ Bind app to db here

    from .views import views
    from .auth import auth

    app.register_blueprint(views)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()

    return app
