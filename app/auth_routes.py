from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from app import db  # Ensure this points to the db initialized in __init__.py
from app.models import User, Doctor
from werkzeug.security import generate_password_hash, check_password_hash
from utils.otp import generate_otp, send_otp, verify_otp 
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, template_folder='templates/auth')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Removed current_app.app_context() wrapper to fix RuntimeError
        data = request.get_json()
        
        # Pulling data from the JSON request
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')

        if not username or not email or not phone or not password:
            return jsonify({"error": "All fields are required."}), 400

        # This query will now work because 'db' is correctly imported
        existing_user = User.query.filter((User.email == email) | (User.phone == phone)).first()
        if existing_user:
            return jsonify({"error": "User with this email or phone already exists."}), 400

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username, # Ensure this column exists in your User model
            email=email,
            phone=phone,
            password=hashed_password,
            role="patient",
            is_verified=False 
        )

        try:
            db.session.add(new_user)
            db.session.commit() # Save to PostgreSQL
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

        # OTP logic remains standard
        otp = generate_otp()
        if send_otp(email, otp):
            session['email'] = email 
            return jsonify({"message": "OTP sent! Redirecting to verify..."}), 200
        else:
            return jsonify({"error": "Error sending OTP."}), 500

    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Checking both tables for the login email
        user = User.query.filter_by(email=email).first() or Doctor.query.filter_by(email_id=email).first()

        if user:
            valid_password = False
            # Check password based on which model was returned
            if isinstance(user, User) and check_password_hash(user.password, password):
                valid_password = True
            elif isinstance(user, Doctor) and user.check_password(password):
                valid_password = True

            if valid_password:
                otp = generate_otp()
                if send_otp(email, otp):
                    session['email'] = email
                    # Default to doctor role if the attribute is missing
                    session['role'] = getattr(user, 'role', 'doctor')
                    return jsonify({"message": "OTP sent to email. Please verify."}), 200
                else:
                    return jsonify({"error": "Error sending OTP."}), 400
            else:
                return jsonify({"error": "Invalid password."}), 400
        else:
            return jsonify({"error": "Invalid email."}), 400

    return render_template('auth/login.html')

@auth_bp.route('/verify_login_otp', methods=['GET', 'POST'])
def verify_login_otp():
    email = session.get('email')
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        user_otp = data.get('otp')

        if not email:
            return jsonify({"error": "Session expired. Please login again."}), 400

        success, message = verify_otp(email, user_otp)

        if success:
            # You can add login_user(user) here if using Flask-Login
            return jsonify({"message": "Verified!", "redirect": url_for('Home')}), 200
        else:
            return jsonify({"error": message}), 400

    # For GET requests, show the page
    return render_template('auth/verify_login_otp.html')

@auth_bp.route('/resend_otp', methods=['GET', 'POST']) # Add GET here
def resend_otp():
    email = session.get('email')
    if not email:
        flash("Session expired, please login again.", "danger")
        return redirect(url_for('auth.login'))
    
    otp = generate_otp()
    if send_otp(email, otp):
        flash("New OTP sent!", "success")
    else:
        flash("Failed to send OTP.", "danger")
    
    # Redirect back to the verification page so they can enter the new code
    return redirect(url_for('auth.verify_login_otp'))

    return jsonify({
    "success": True, 
    "message": "Verified!", 
    "redirect_url": url_for('Home')
}), 200
@auth_bp.route('/logout')
def logout():
    session.clear()  # This removes the email and role from the session
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))