from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    # Configuración del proyecto
    app.config.from_mapping(
        DEBUG = False,
        SECRET_KEY = 'Clockapp2024$icsecompany',
        SQLALCHEMY_DATABASE_URI = "sqlite:///clockapp.db"
    )

    #Instancia de SQLAlchemy
    db.init_app(app)

    from clock import home
    app.register_blueprint(home.bp)

    from clock import dashboard
    app.register_blueprint(dashboard.bp)
    
    from clock import auth
    app.register_blueprint(auth.bp)


    with app.app_context():
        db.create_all()

    return app