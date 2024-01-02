from flask import Flask, jsonify, request
import json
from supabase import create_client, Client
import traceback
from datetime import datetime

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
    error = False

    if (not email) or (len(email) < 5):
        error = 'Email needs to be valid'

    if (not error) and ((not password) or (len(password) < 5)):
        error = 'Provide a password'

    if not error:
        # Fetch user by email
        response = supabase.table('users').select("*").ilike('email', email).execute()

        if len(response.data) > 0:
            user = response.data[0]

            # Compare hashed password
            if user['password'] == password: 
                return json.dumps({'status': 200, 'message': '', 'data': user})
            else:
                error = 'Invalid Email or password'

    if error:
        return json.dumps({'status': 500, 'message': error})

    return json.dumps({'status': 500, 'message': 'Invalid Email or password'})

@app.route('/api/user_signup', methods=['GET', 'POST'])
def api_user_signup():
    email= request.form.get('email')
    password= request.form.get('password')
    error =False

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'