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


@app.route('/api/user_login', methods=['POST', 'GET'])
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
    # Compare plain text password based on the table (user or provider)
    if 'password' in user and user['password'] == password:
        return jsonify({'status': 200, 'message': 'Login successful', 'data': user}), 200
    else:
        return jsonify({'status': 401, 'message': 'Invalid email or password'}), 401
    

@app.route('/api/signup_user', methods=['POST'])
def api_signup_user():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Add validation checks for email, password, and confirm_password
    if not email or len(email) < 5:
        return jsonify({'status': 400, 'message': 'Email needs to be valid'}), 400

    if not password or len(password) < 5:
        return jsonify({'status': 400, 'message': 'Provide a valid password'}), 400

    if password != confirm_password:
        return jsonify({'status': 400, 'message': 'Passwords do not match'}), 400

    # Check if the user already exists
    user_exists_response = supabase.table('user').select("*").ilike('email', email).execute()

    if len(user_exists_response.data) > 0:
        return jsonify({'status': 400, 'message': 'User with this email already exists'}), 400

    # Insert the new user into the 'user' table
    response = supabase.table('user').insert([
        {'email': email, 'password': password},
    ]).execute()
    
    user_id = response['data'][0]['id']
    print("User data inserted:", response)

    if user_id:
        # Successfully inserted user, proceed to signup_user1
        return jsonify({'status': 200, 'message': 'User signup successful', 'user_id': user_id}), 200
    else:
        # Failed to insert user
        return jsonify({'status': 500, 'message': 'Internal Server Error'}), 500
    
@app.route('/api/signup_provider', methods=['POST'])
def api_signup_provider():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Add validation checks for email, password, and confirm_password if needed
    if not email or len(email) < 5:
        return jsonify({'status': 400, 'message': 'Email needs to be valid'}), 400

    if not password or len(password) < 5:
        return jsonify({'status': 400, 'message': 'Provide a valid password'}), 400

    if password != confirm_password:
        return jsonify({'status': 400, 'message': 'Passwords do not match'}), 400

    # Check if the provider already exists
    provider_exists_response = supabase.table('provider').select("*").ilike('email', email).execute()

    if len(provider_exists_response.data) > 0:
        return jsonify({'status': 400, 'message': 'Provider with this email already exists'}), 400

    # Insert the new provider into the 'provider' table
    response = supabase.table('provider').insert([
        {'email': email, 'password': password},
    ]).execute()
    
    provider_id = response['data'][0]['id']


    return jsonify({'status': 200, 'message': 'Provider signup successful', 'id':provider_id}), 200

@app.route('/api/signup_user1', methods=['POST'])
def api_signup_user1():
    user_id = request.form.get('id')
    name = request.form.get('name')
    surname = request.form.get('surname')
    username = request.form.get('username')
    wilaya = request.form.get('wilaya')
    phone_number = request.form.get('phone_number')
    
    #add validation forms
    if not name:
        return jsonify({'status': 400, 'message': 'name must be filled'}), 400
    elif not surname :
        return jsonify({'status': 400, 'message': 'surname must be filled'}), 400
    elif not username:
        return jsonify({'status': 400, 'message': 'username must be filled'}), 400
    elif not wilaya:
        return jsonify({'status': 400, 'message': 'wilaya must be filled'}), 400
    elif not phone_number:
        return jsonify({'status': 400, 'message': 'phone_number must be filled'}), 400
    elif len(phone_number) != 10:
        return jsonify({'status': 400, 'message': 'phone_number must be 10 digits'}), 400
    elif not phone_number.isdigit():
        return jsonify({'status': 400, 'message': 'phone_number must be digits'}), 400
    elif not phone_number.startswith('0'):
        return jsonify({'status': 400, 'message': 'phone_number must start with 0'}), 400
    elif not phone_number.startswith('05') and not phone_number.startswith('06') and not phone_number.startswith('07'):
        return jsonify({'status': 400, 'message': 'phone_number must start with 05 or 06 or 07'}), 400
    
    #add the data to the table user based on the user id
    response = supabase.table('user').insert([
        {'id': user_id, 'name': name, 'surname': surname, 'username': username, 'wilaya': wilaya, 'phone_number': phone_number},
    ]).execute()
    
    return jsonify({'status': 200, 'message': 'User signup part 1 successful', 'id': user_id}), 200


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
    
@app.route('/gifts.create',methods=['GET','POST'])
def api_gifts_create():    
    print('Variables...'+str(request.args))
    if request.args.get('gifts'):
        try:
            gifts=json.loads(str(request.args.get('gifts')))
            mapping={}
            for gift in gifts:
                print('Creating a gift with the name '+gift['name'])
                mapping[gift['id']]=gift['id']
            data={'status':'OK','message':'success','mapping':mapping}
            return json.dumps(data)
        except Exception as error:
            print(str(error))
            data={'status':'Error','message':'Exception ...','mapping':[]}
            return json.dumps(data)            
    data={'status':'Error','message':'No data','mapping':[]}
    return json.dumps(data)     


@app.route('/gifts.get', methods=['GET'])
def get_gifts():
    table_name = 'gifts'
    response = supabase.table(table_name).select('*').execute()
    gifts_list = response.data


    for gift in gifts_list:
        product_images=supabase.table('images').select('*').eq('product_id', gift['id']).execute()
        gift['images']=product_images.data
        product_colors = supabase.table('product_color').select('*').eq('product_id', gift['id']).execute()
        gift['colors']=product_colors.data
    
    # #  Fetch 'isFavorite' information from userFavorites table
    # for gift in gifts_list:
    #     user_id = 1  # Replace with the actual user ID or fetch it dynamically
    #     is_favorite_response = supabase.table('user_favorites').select('*').eq('user_id', user_id).eq('product_id', gift['id']).execute()
    #     if is_favorite_response != None:
    #         is_favorite_data = is_favorite_response.data
    #         gift['isFavorite'] = bool(is_favorite_data)
    #     else:
    #         gift['isFavorite'] = False

    return jsonify(gifts=gifts_list)


# # ********

# @app.route('/gifts.get', methods=['GET'])
# def get_gifts():
#     table_name = 'gifts'

#     # Modify the SQL query to get the desired information
#     query = f'''
#         SELECT 
#             gifts.id,
#             gifts.name,
#             gifts.description,
#             gifts.price,
#             gifts.category,
#             MAX(images.imagePath) as imagePath,
#             MAX(images.type) as type
#         FROM {table_name}
#         LEFT JOIN images ON gifts.id = images.product_id
#         GROUP BY gifts.id
#         ORDER BY gifts.name ASC
#     '''

#     # Execute the query using Supabase
#     response = supabase.query(query)

#     # Extract data from the response
#     gifts_list = response['data']

# #  Fetch 'isFavorite' information from userFavorites table
#     for gift in gifts_list:
#         user_id = 1  # Replace with the actual user ID or fetch it dynamically
#         is_favorite_response = supabase.table('userFavorites').select('*').eq('user_id', user_id).eq('gift_id', gift['id']).execute()
#         is_favorite_data = is_favorite_response['data']
#         gift['isFavorite'] = len(is_favorite_data) > 0

#     # Return the modified data as JSON
#     return jsonify(gifts=gifts_list)
# # *****

# @app.route('/gifts.add', methods=['POST'])
# def add_gift():
#     try:
#         new_gift = request.json
#         table_name = 'gifts'
#         response = supabase.table(table_name).upsert([new_gift]).execute()
#         return jsonify(success=True, id=response.data[0]['id'])
#     except Exception as e:
#         return jsonify(success=False, error=str(e))

# from datetime import datetime

@app.route('/gifts.add', methods=['POST'])
def add_gift():
    try:
        new_gift = request.json
        table_name = 'gifts'

        # Extract colors and images from new_gift
        colors = new_gift.pop('colors', [])
        images = new_gift.pop('images', [])

        # Insert into the gifts table
        response = supabase.table(table_name).upsert([new_gift]).execute()
        gift_id = response.data[0]['id']

        colors_list = []
        # Insert colors into product_color table
        for color in colors:
            # color['product_id'] = gift_id
            # color['create_date'] = datetime.now().isoformat()
            # colors_list.add({'product_id': gift_id, 'create_date': datetime.now().isoformat(), 'color': color})
            supabase.table('product_color').upsert([{'product_id': gift_id, 'create_date': datetime.now().isoformat(), 'color': color}]).execute()

        # Insert images into images table
        for image in images:
            image['product_id'] = gift_id
            image['create_date'] = datetime.now().isoformat()
            supabase.table('images').upsert([image]).execute()

        return jsonify(success=True, id=gift_id)
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/gifts.get_by_id/<int:gift_id>', methods=['GET'])
def get_gift_by_id(gift_id):
    try:
        table_name = 'gifts'
        response = supabase.table(table_name).select('*').eq('id', gift_id).single().execute()
        gift_data = response.data
        return jsonify(gift=gift_data)
    except Exception as e:
        return jsonify(error=str(e))

@app.route('/gifts.update/<int:gift_id>', methods=['PUT'])
def update_gift(gift_id):
    try:
        updated_gift = request.json
        table_name = 'gifts'
        response = supabase.table(table_name).upsert([updated_gift]).eq('id', gift_id).execute()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/gifts.delete/<int:gift_id>', methods=['DELETE'])
def delete_gift(gift_id):
    try:
        table_name = 'gifts'
        response = supabase.table(table_name).delete().eq('id', gift_id).execute()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))       


@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'


# if __name__ == '__main__':
#     app.run(debug=True)
    