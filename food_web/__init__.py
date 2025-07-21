from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate

db = SQLAlchemy()  # ✅ SINGLE INSTANCE
migrate = Migrate()  

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'food_app'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

    db.init_app(app)  # ✅ Bind app to db here
    migrate.init_app(app, db)

    from .views import views
    from .auth import auth

    app.register_blueprint(views)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()

    return app
