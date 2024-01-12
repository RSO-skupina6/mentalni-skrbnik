#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_restful import Api, Resource, reqparse
import requests
import asyncio
import os

app = Flask(__name__)

auth_service_url = 'http://34.118.27.140:6734'
msg_service_url = 'http://34.116.192.107:8573'
forum_service_url = 'http://34.116.254.116:3000'

secret_engine_id = os.environ['SEARCH_ENGINE_ID']
secret_api_key = os.environ['SEARCH_API_KEY']

joke_api_url = 'https://v2.jokeapi.dev/joke/Any'

jokeapi_circuit_breaker = True
async def async_set_retry(timeout):
    await asyncio.sleep(timeout)
    global jokeapi_circuit_breaker
    jokeapi_circuit_breaker = True

def get_joke() -> str:
    global jokeapi_circuit_breaker
    generic_joke = "It appears that jokeAPI developers are having a good time fixing this joke. Please visit later..."
    if jokeapi_circuit_breaker:
        try:
            response = requests.get(joke_api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data['type'] == 'single':
                    joke = data['joke']
                    joke = f"Here's a joke for you: {joke}"
                elif data['type'] == 'twopart':
                    setup = data['setup']
                    delivery = data['delivery']
                    joke = f"Joke Setup: {setup}"
                    joke += f"Joke Delivery: {delivery}"
                else:
                    joke = "No joke found"
            else:
                joke = generic_joke
        except Exception:
            jokeapi_circuit_breaker = False
            asyncio.run(async_set_retry(60))
            joke = generic_joke
    else:
        joke = generic_joke
    return joke


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


@app.route('/logout', methods=['POST'])
def logout():
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=str, required=True)
    parser.add_argument('cookie', type=str, required=True)
    args = parser.parse_args()
    id = args['id']
    cookie = args['cookie']
    
    # Send logout request to authService
    logout_data = {'id': id, 'cookie': cookie}
    response = requests.post(f'{auth_service_url}/logout', json=logout_data, headers={'Content-Type': 'application/json'})
    
    if response.status_code == 201:
        # Logout successful
        return 'Logout successful.', 201
    # Logout failed
    return 'Logout unsuccessful.', 401

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

@app.route('/forums')
def forums():
    return render_template('forums.html')

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

@app.route('/get-joke', methods=['GET'])
def get_joke_endpoint():
    joke = get_joke()  # Call your function to retrieve a joke
    return jsonify({'joke': joke})

@app.route('/messages/<username>', methods=['GET'])
def get_messages(username):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authorization token missing'}), 401
    response = requests.get(f'{msg_service_url}/messages/{username}', headers={'Authorization': token})
    
    if response.status_code == 200:
        return jsonify(response.json()), 200
    
    return jsonify({'message': 'Error retrieving messages'}), 500

from flask import request, jsonify

@app.route('/message', methods=['POST'])
def send_message():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authorization token missing'}), 401
    
    data = request.get_json()

    sender = data.get('sender')
    receiver = data.get('receiver')
    message = data.get('message')

    if not (sender and receiver and message):
        return jsonify({'message': 'Missing sender, receiver, or message'}), 400

    # Assuming the 'hash' is not required and is generated on the backend
    response = requests.post(
        f'{msg_service_url}/message',
        json={'sender': sender, 'receiver': receiver, 'message': message, 'hash': token},
        headers={'Authorization': token}
    )
    
    if response.status_code == 200:
        return jsonify(response.json()), 200
    
    return jsonify({'message': 'Error sending message'}), 500

@app.route('/google-search', methods=['GET'])
def google_search():
    query = request.args.get('q')
    if not query:
        return jsonify({'message': 'Missing search query'}), 400

    api_key = secret_api_key
    cx = secret_engine_id

    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}'
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        search_results = response.json().get('items', [])
        return jsonify({'results': search_results}), 200
    else:
        return jsonify({'message': 'Error performing Google search'}), response.status_code


if __name__ == '__main__':
    app.run(debug=True, port=443)