from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_login import login_required, current_user, login_user, logout_user, LoginManager
from werkzeug.security import generate_password_hash
from datetime import datetime
import pickle
import pandas as pd
import numpy as np
from db import db,app
from forms import LoginForm, RegistrationForm, PredictForm
from urllib.parse import quote_plus


app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

model = pickle.load(open('ml_model.pkl', 'rb'))
def predictor(to_predict_list):
    to_predict = np.array(to_predict_list).reshape(1, -1)
    result = model.predict(to_predict)
    return result[0]


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            to_predict_list = request.form.to_dict()  # Collect form data as a dictionary
            to_predict_list = list(to_predict_list.values())  # Get the values from the dictionary
            to_predict_list = [int(value) for value in to_predict_list]  # Convert all values to integers
            
            # Call the predictor function
            result = predictor(to_predict_list)        
            prediction = 'Unsafe' if int(result) == 1 else 'Safe'
            
            return render_template("predict.html", prediction=prediction)
        except ValueError as e:
            # Handle invalid input gracefully
            flash(f"Invalid input: {str(e)}", 'danger')
            return render_template("predict.html", prediction="Error in input. Please check your entries.")
    
    return render_template("predict.html")

test_input = np.array([[1,	2,	3,	2,	2,	2,	3,	2]])  # Example input
print("Test prediction:", model.predict(test_input))


from twilio.rest import Client

account_sid = 'your_account_sid'
auth_token = 'Your_auth_token'
client = Client(account_sid, auth_token)

@app.route('/send_sos', methods=['POST'])
def send_sos():
    try:
        # Send the SOS message
        message = client.messages.create(
            messaging_service_sid='your_messageing_service_sid',
            body='This is an SOS alert from Guardia! Immediate assistance required.',
            to='phone_number'
        )
        
        # Return a success response
        return jsonify({"message": "Message sent successfully!"}), 200


    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Failed to send SOS alert. Please try again later.'}), 500


# Login manager user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.query.get(int(user_id))


# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method =='POST':
       name=request.form['name']
       pwd=request.form['password']

       cur=db.connection.cursor()
       cur.execute(f"insert into tbl_users(username,password)values('{name}','{pwd}')")
       db.connection.commit()
       cur.close
       
       return redirect(url_for('login'))
    
    return render_template('register.html')
    


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = db.connection.cursor()
        cur.execute("SELECT email, password FROM user WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and password == user[1]:
            session['email'] = email
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')


# Profile route (only accessible to logged-in users)
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


# Edit profile route
@app.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    current_user.name = request.form['name']
    current_user.email = request.form['email']
    current_user.phone = request.form['phone']
    current_user.emergency_contacts = request.form['emergency_contacts']
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))


# Logout route
@app.route('/logout')
@login_required
def logout():
    session.pop('username',None)
    return redirect(url_for('home'))


# Routes for other pages
@app.route('/map')
def map():
    return render_template('map.html')


@app.route('/about')
def about():
    return render_template('about.html')


# Home route
@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
