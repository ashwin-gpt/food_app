from food_web import create_app, db  # Make sure db is defined in __init__.py of food_web
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

