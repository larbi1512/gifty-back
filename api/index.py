from flask import Flask, jsonify, request
import json
from supabase import create_client, Client
import traceback
from datetime import datetime
from werkzeug.security import check_password_hash


SUPABASE_URL = 'https://zkfovcmkaobvsceazqat.supabase.co'
SUPABASE_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InprZm92Y21rYW9idnNjZWF6cWF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDI2NjIwNDIsImV4cCI6MjAxODIzODA0Mn0.p7nCDkbdLK9WnfrmELj8zDk4dfTsP1DveSMHeGnrPpA'

app = Flask(__name__)
supabase =  create_client(SUPABASE_URL, SUPABASE_API_KEY)

data = [
    {'id': 1, 'name': 'Item 1'},
    {'id': 2, 'name': 'Item 2'},
    {'id': 3, 'name': 'Item 3'},
]

@app.route('/api/get_users', methods=['GET'])
def get_users():
    table_name = 'user'
    response = supabase.table(table_name).select('*').execute()
    user_list = response.data
    print('heeeeeeere')
    print(response)
    return  jsonify(users = user_list)


@app.route('/api/user_login', methods=['POST'])
def api_users_login():
    email = request.form.get('email')
    password = request.form.get('password')
    error = None

    if not email or len(email) < 5:
        error = 'Email needs to be valid'

    if not password or len(password) < 5:
        error = 'Provide a valid password'

    if error:
        return jsonify({'status': 400, 'message': error}), 400

    # Try fetching user from 'user' table
    response_user = supabase.table('user').select("*").ilike('email', email).execute()

    # If user is not found in 'user' table, try fetching from 'provider' table
    if len(response_user.data) == 0:
        response_user = supabase.table('provider').select("*").ilike('email', email).execute()

    if len(response_user.data) == 0:
        return jsonify({'status': 404, 'message': 'Email not found'}), 404

    user = response_user.data[0]

    # Check for password in both 'user' and 'provider' tables
    if 'password' not in user:
        # Try fetching password from 'provider' table
        response_password = supabase.table('provider').select("password").ilike('email', email).execute()
        
        if len(response_password.data) == 0:
            return jsonify({'status': 500, 'message': 'Password column missing in user/provider table'}), 500

        user['password'] = response_password.data[0]['password']

    # Compare hashed password
    if not check_password_hash(user['password'], password):
        return jsonify({'status': 401, 'message': 'Invalid email or password'}), 401

    return jsonify({'status': 200, 'message': 'Login successful', 'data': user}), 200


@app.route('/api/user_signup', methods=['GET', 'POST'])
def api_user_signup():
    email= request.form.get('email')
    password= request.form.get('password')
    error =False


@app.route('/isEmailExists', methods=['GET'])
def is_email_exists():
    email = request.args.get('email')

    if not email or len(email) < 5:
        return json.dumps({'status': 400, 'message': 'Email needs to be valid'}), 400

    response = supabase.table('user').select("*").ilike('email', email).execute()

    if len(response.data) > 0:
        return json.dumps({'status': 200, 'message': 'Email exists'}), 200
    else:
        return json.dumps({'status': 404, 'message': 'Email does not exist'}), 404
@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'