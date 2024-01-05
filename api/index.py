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
    app.run(debug=True)
    