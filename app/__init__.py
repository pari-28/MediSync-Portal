from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

# Initialize global extensions
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()  

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    logging.basicConfig(level=logging.DEBUG)

    # Database and app configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')



    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'parisangamnerkar@gmail.com'
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_DEFAULT_SENDER'] = 'parisangamnerkar@gmail.com'

    # Razorpay configuration
    app.config['RAZORPAY_KEY_ID'] = os.getenv('RAZORPAY_KEY_ID')
    app.config['RAZORPAY_KEY_SECRET'] = os.getenv('RAZORPAY_KEY_SECRET')

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    mail.init_app(app)
    
    # Initialize Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Matches BlueprintName.FunctionName

    # Use the app context to perform initialization tasks
    with app.app_context():
        # Import models so they are registered with SQLAlchemy
        from .models import User, Doctor, PatientRecord, Appointment, PrescriptionRecord, MedicalTest
        
        # Define user_loader inside context
        @login_manager.user_loader
        def load_user(user_id):
            # Check User table (Integer ID)
            user = User.query.get(int(user_id))
            if user:
                return user
            # Check Doctor table (String ID)
            return Doctor.query.get(user_id)

        # Register blueprints inside context
        from app.doctor_routes import doctor_bp
        from app.patient_routes import patient_bp
        from app.auth_routes import auth_bp
        from app.admin_routes import admin as admin_bp # Import your admin blueprint
        from app.payment_routes import payment_bp

        app.register_blueprint(doctor_bp, url_prefix='/doctor')
        app.register_blueprint(patient_bp, url_prefix='/patient')
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(payment_bp, url_prefix='/payments')

    @app.route('/', methods=['GET'])
    def Home():
        return render_template('index.html')
    
    return app