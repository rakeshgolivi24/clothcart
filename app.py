import os
from flask import Flask
from database.models import db, User, Category, Product
from routes.public import public_bp
from routes.admin import admin_bp
from flask import render_template

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "CHANGE_THIS_SECRET"
    # For dev: SQLite; later swap to PostgreSQL/MySQL
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'clothcart.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    with app.app_context():
        db.create_all()
        seed_default_data()
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500
    return app




def seed_default_data():
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin")
        admin.set_password("admin123")  # change later
        db.session.add(admin)

    if Category.query.count() == 0:
        men = Category(name="Men", slug="men")
        women = Category(name="Women", slug="women")
        kids = Category(name="Kids", slug="kids")
        db.session.add_all([men, women, kids])

    db.session.commit()


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
