from flask import Flask, jsonify, request
import json
from supabase import create_client, Client
import traceback
from datetime import datetime
import os
import tempfile


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
    role = 'user' if 'user_id' in user else 'provider'
    id_field = f'{role}_id'
    
    # Extract the user ID from the response
    user_id = user[id_field]

    # Compare plain text password based on the table (user or provider)
    if 'password' in user and user['password'] == password:
        return jsonify({'status': 200, 'message': 'Login successful', 'data': {'user': user,'role': role, 'user_id': user_id}}), 200
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
    
    print("User data inserted:", response)

    if len(response.data)>0:
        # Successfully inserted user, proceed to signup_user1
        user_id = response.data[0]['user_id']
        return jsonify({'status': 200, 'user_id': user_id, 'message': 'User signup successful'}), 200
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
    
    print("Provider data inserted:", response)

    if len(response.data)>0:
        # Successfully inserted user, proceed to signup_provider1
        provider_id = response.data[0]['provider_id']
        return jsonify({'status': 200, 'provider_id': provider_id, 'message': 'Provider signup successful'}), 200
    else:
        # Failed to insert provider
        return jsonify({'status': 500, 'message': 'Internal Server Error'}), 500



@app.route('/api/signup_user1', methods=['POST'])
def api_signup_user1():
    user_id = request.form.get('user_id')
    print("Received user_id in api_signup_user1:", user_id)
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
    response = supabase.table('user').update([
        {'name': name, 'username': username, 'wilaya': wilaya, 'phone_number': phone_number},
    ]).eq('user_id', user_id).execute()
    
    return jsonify({'status': 200, 'message': 'User signup part 1 successful'}), 200


@app.route('/api/signup_provider1', methods=['POST'])
def api_provider_user1():
    provider_id = request.form.get('provider_id')
    print("Received provider_id in api_provider_user1:", provider_id)
    store_name = request.form.get('store_name')
    location = request.form.get('location')
    phone_number = request.form.get('phone_number')
    category = request.form.get('category')
    
    #add validation forms
    if not store_name:
        return jsonify({'status': 400, 'message': 'username must be filled'}), 400
    elif not location:
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
    elif not category:
        return jsonify({'status': 400, 'message': 'category must be filled'}), 400
 
    
    
    #add the data to the table provider based on the provider id
    response = supabase.table('provider').update([
        {'store_name': store_name, 'location': location, 'phone_number': phone_number, 'category': category,},
    ]).eq('provider_id', provider_id).execute()
    
    return jsonify({'status': 200, 'message': 'User signup part 1 successful'}), 200


def upload_user_image(file, user_id):
    try:
        print("Attempting to upload image to Supabase Storage for user...")

        # Save the temporary file to a known location
        temp_file_path = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(temp_file_path)

        # Upload the file to Supabase Storage
        storage_response = supabase.storage.from_('user_pic').upload(file.filename, file=temp_file_path)
        print("File uploaded:", file.filename)

        if storage_response.status_code != 200:
            raise Exception(f"Failed to upload image. Status code: {storage_response.status_code}")

        # Extract metadata from the response
        metadata = storage_response.json()

        # Construct the image URL using the metadata
        image_url = f"{SUPABASE_URL}/storage/v1/object/{metadata['Key']}"
        if not image_url:
            raise Exception("Image URL not found in the response")

        print("Image URL:", image_url)

        # Update the user profile with the image URL
        response = supabase.table('user').update({
            'profile_pic': image_url
            
        }).eq('user_id', user_id).execute()

        if 'error' in response and response['error'] is not None:
            raise Exception(f"Failed to update user profile: {response['error']['message']}")

        print("User profile updated successfully.")

        return image_url

    except Exception as e:
        print(f"Exception during image upload for user: {e}")
        raise

    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)


def upload_provider_image(file, provider_id):
    try:
        print("Attempting to upload image to Supabase Storage for provider...")

        # Save the temporary file to a known location
        temp_file_path = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(temp_file_path)

        # Upload the file to Supabase Storage
        storage_response = supabase.storage.from_('user_pic').upload(file.filename, file=temp_file_path)
        print("File uploaded:", file.filename)

        if storage_response.status_code != 200:
            raise Exception(f"Failed to upload image. Status code: {storage_response.status_code}")

        # Extract metadata from the response
        metadata = storage_response.json()

        # Construct the image URL using the metadata
        image_url = f"{SUPABASE_URL}/storage/v1/object/{metadata['Key']}"
        if not image_url:
            raise Exception("Image URL not found in the response")

        print("Image URL:", image_url)

        # Update the provider profile with the image URL
        response = supabase.table('provider').update({
            'brand_pic': image_url
        }).eq('provider_id', provider_id).execute()

        if 'error' in response and response['error'] is not None:
            raise Exception(f"Failed to update provider profile: {response['error']['message']}")

        print("Provider profile updated successfully.")

        return image_url

    except Exception as e:
        print(f"Exception during image upload for provider: {e}")
        raise

    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)


@app.route('/api/finish_signup_user', methods=['POST'])
def finish_signup_user():
    try:
        user_id = request.form.get('user_id')
        
        print("Received user_id in finish_signup_user:", user_id)

        # Check if an image file is included in the request
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and file:
                print("File received:", file.filename)
                print("Attempting to upload image to Supabase Storage for user...")

                # Upload image and update user profile
                image_url = upload_user_image(file, user_id)
                print("Image URL is:", image_url)

        return jsonify({'status': 200, 'message': 'Signup process completed successfully'}), 200

    except Exception as e:
        return jsonify({'status': 500, 'message': str(e)}), 500


@app.route('/api/finish_signup_provider', methods=['POST'])
def finish_signup_provider():
    try:
        provider_id = request.form.get('provider_id')
        facebook = request.form.get('facebook')
        instagram = request.form.get('instagram')
        website = request.form.get('website')
        print("Received provider_id in finish_signup_provider:", provider_id)

        # Check if an image file is included in the request
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and file:
                print("File received:", file.filename)
                print("Attempting to upload image to Supabase Storage for provider...")

                # Upload image and update provider profile
                image_url = upload_provider_image(file, provider_id)
                print("Image URL is:", image_url)
                
                response = supabase.table('provider').update({
            'facebook': facebook,
            'instagram': instagram,
            'website': website }).eq('provider_id', provider_id).execute()

        return jsonify({'status': 200, 'message': 'Signup process completed successfully'}), 200

    except Exception as e:
        return jsonify({'status': 500, 'message': str(e)}), 500


@app.route('/api/get_user_data', methods=['GET'])
def get_user_data():
    user_id = request.args.get('user_id')

    # Fetch user data from the 'user' table
    user_data_response = supabase.table('user').select("*").eq('user_id', user_id).execute()

    if len(user_data_response.data) == 0:
        return jsonify({'status': 404, 'message': 'User not found'}), 404

    user_data = user_data_response.data[0]
    return jsonify(user_data), 200

@app.route('/api/get_provider_data', methods=['GET'])
def get_provider_data():
    provider_id = request.args.get('provider_id')

    # Fetch provider data from the 'provider' table
    provider_data_response = supabase.table('provider').select("*").eq('provider_id', provider_id).execute()

    if len(provider_data_response.data) == 0:
        return jsonify({'status': 404, 'message': 'Provider not found'}), 404

    provider_data = provider_data_response.data[0]
    return jsonify(provider_data), 200

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


if __name__ == '__main__':
    app.run(debug=True,host="10.80.5.52")
    