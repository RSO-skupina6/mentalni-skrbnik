#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

app = Flask(__name__)

auth_service_url = 'http://34.118.27.140:6734'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Send login request to authService
        response = requests.post(f'{auth_service_url}/auth', json={'username': username, 'password': password})
        
        if response.status_code == 201:
            # Authentication successful, extract token and send it as JSON
            token = response.json().get('token')  # Assuming token is in JSON response
            if token:
                return jsonify({'token': token})
            else:
                return 'Token not found in response', 500  # Some error handling
            
        # Authentication failed
        return 'Invalid credentials. Please try again.', 401

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Send registration request to authService
        response = requests.post(f'{auth_service_url}/register', json={'username': username, 'password': password})
        
        if response.status_code == 201:
            # Registration successful
            return redirect(url_for('login'))  # Redirect to login page after successful registration
        
        # Registration failed
        return 'Registration failed. Username might already exist.'

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/user-info', methods=['GET'])
def get_user_info():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authorization token missing'}), 401
    
    response = requests.get(f'{auth_service_url}/userinfo', headers={'Authorization': token})
    
    if response.status_code == 200:
        return jsonify(response.json()), 200
    
    return jsonify({'message': 'Error retrieving user info'}), 500

@app.route('/list-users', methods=['GET'])
def get_active_users():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authorization token missing'}), 401
    
    response = requests.get(f'{auth_service_url}/listonlineusers', headers={'Authorization': token})
    
    if response.status_code == 200:
        return jsonify(response.json()), 200
    
    return jsonify({'message': 'Error retrieving active users'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=443)