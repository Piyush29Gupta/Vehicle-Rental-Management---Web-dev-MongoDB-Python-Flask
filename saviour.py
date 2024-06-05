from flask import Flask, render_template, request, session
from pymongo import MongoClient

car = 200
bike = 100
scooty = 80
cycle = 50
mini_bus = 500




client = MongoClient('mongodb://localhost:27017/')
py_mongodb = client['py_mongodb'] #database

py_mongodb_collection_login = py_mongodb['py_mongodb_collection_login']

py_mongodb_collection_customer = py_mongodb['py_mongodb_collection_customer']

py_mongodb_collection_rent_list = py_mongodb['py_mongodb_collection_rent_list']

# py_mongodb_collection_rent_list.insert_one({'car':200,'bike':100,'scooty':80,'cycle':50,'mini_bus':500})




app = Flask(__name__, template_folder='C:/Users/Piyush Gupta/OneDrive/Desktop/connection mongo with vs python/BDS project Mongo')
app.secret_key = '2914@piyush@gupta@pyhton_flask_mongodb'

@app.route('/')
def app_start():
    
    return render_template('Login_page.html')

@app.route('/submit',methods=['POST'])
def login_details():
    
    login_id = request.form['login_id']
    login_pwd = request.form['login_pwd']

    session['login_id'] = login_id

    match_details = py_mongodb_collection_login.find_one({'login_id':login_id,'login_pwd':login_pwd})

    if match_details:
        # return render_template('customer_details.html')
        return render_template('customer_details.html')

    else:
        return "<strong>Wrong UserId Or Password!!! Go To Sign-in Page</strong>"

    # insert_login_details={
    #     'login_id' : login_id,
    #     'login_pwd' : login_pwd
    # }

    # py_mongodb_collection_login.insert_one(insert_login_details)
    
    



@app.route('/sign_in',methods=['POST'])
def goto_sign_in_page():
    return render_template('Sign_in_page.html')

@app.route('/login-btn_from_sign_in',methods=['POST'])
def goto_login_from_sign_in():
    return render_template('Login_page.html')

@app.route('/submit_sign_in',methods=['POST'])
def sign_in_details():
    user_name = request.form['user_name']
    login_id = request.form['login_id']
    login_pwd = request.form['login_pwd']
    Confirm_password = request.form['Confirm_password']
    session['login_id'] = login_id
    if Confirm_password == login_pwd:
        if user_exists(login_id)==1:
            return "<strong>User is Already exixts with this Login Id, Please Login From The Login Page</strong>"

        else:
            py_mongodb_collection_login.insert_one({'User Name':user_name,'login_id':login_id,'login_pwd':login_pwd})
            return render_template('customer_details.html')
    
    else:
        return "<strong>Password Mismatch, TRY AGAIN!!!</strong>"


def user_exists(login_id):
    criteria = {'login_id':login_id}

    check_user = py_mongodb_collection_login.count_documents(criteria)

    if check_user>0:
        return 1
    
    else:
        return 0

@app.route('/goto_mongo_operations_from_customer_details',methods=['POST'])
def goto_mongo_operations_from_customer_details():
    return render_template('mongo_operations.html') 


@app.route('/submit_form',methods=['POST'])
def customer_details():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    age = request.form['age']
    licence = request.form['licence']
    vehicles = request.form.getlist('vehicle')

    vehicles_array = [{'vehicle':vehicle} for vehicle in vehicles]

    hours_str = request.form['hours']

    hours = int(hours_str)
    
    login_id = session.get('login_id')

    
    insert_customer_details = {
    'Login id':login_id,
    'First Name':first_name,
    'Last Name':last_name,
    'Age':age,
    'Licence':licence,
    'Vehicles':vehicles_array,
    'Hours' : hours,
    'total_amount':None,
    'due_amount':None,
    'deposit_amount':None
    }

    py_mongodb_collection_customer.insert_one(insert_customer_details)
    return render_template('mongo_operations.html') 

    # return login_id
    
@app.route('/show_details', methods=['POST'])
def show_customer_details():
    login_id = session.get('login_id')

    customer_data = py_mongodb_collection_customer.find_one({'Login id': login_id}, {'_id': False})

    if customer_data:
            
        first_name = customer_data.get('First Name', '')
        last_name = customer_data.get('Last Name', '')
        age = customer_data.get('Age', '')
        licence = customer_data.get('Licence', '')
        hours = customer_data.get('Hours', '')

        vehicles = customer_data.get('Vehicles', [])
            
        return print_details(first_name,last_name,age,licence,hours,vehicles)
    
    else:
        return "<strong>Customer Data Not Found!!!</strong>"

def print_details(first_name, last_name, age, licence, hours, vehicles):
    
    string = (
        f"<strong>First Name:</strong> {first_name}<br><br>"
        f"<strong>Last Name:</strong> {last_name}<br><br>"
        f"<strong>Age:</strong> {age}<br><br>"
        f"<strong>Licence:</strong> {licence}<br><br>"
        f"<strong>Hours:</strong> {hours}<br><br>"
    )

    vehicle_types = [vehicle['vehicle'] for vehicle in vehicles]
    vehicle_string = f"<strong>Vehicles:</strong> {', '.join(vehicle_types)}"

    return string + vehicle_string


@app.route('/show_rent_amount', methods=['POST'])
def show_rent_amount():
    login_id = session.get('login_id')
    customer_rent_hours = py_mongodb_collection_customer.find_one({'Login id': login_id}, {'Hours': 1,'Vehicles': 1, '_id': 0})
    customer_rent_vehicles = py_mongodb_collection_customer.find_one({'Login id': login_id}, {'Vehicles': 1, '_id': 0})
    
    hours = customer_rent_hours.get('Hours', 0)
    total_amount = 0
   
    for vehicle in customer_rent_vehicles['Vehicles']:
        if vehicle['vehicle'] == 'CAR':
            total_amount += hours * car
        elif vehicle['vehicle'] == 'BIKE':
            total_amount += hours * bike
        elif vehicle['vehicle'] == 'SCOOTY':
            total_amount += hours * scooty
        elif vehicle['vehicle'] == 'CYCLE':
            total_amount += hours * cycle
        elif vehicle['vehicle'] == 'MINI-BUS':
            total_amount += hours * mini_bus

    py_mongodb_collection_customer.update_one({'Login id': login_id}, {'$set': {'total_amount': total_amount}})

    customer_total_amount = py_mongodb_collection_customer.find_one({'Login id': login_id}, {'total_amount': 1,'deposit_amount':1, '_id': 0})

    value_customer_total_amount = customer_total_amount.get('total_amount','')
    value_deposit_amount = customer_total_amount.get('deposit_amount','')

    return f"<strong>Total Amount : </strong>{value_customer_total_amount} <br><strong>Deposited Amount : </strong>{value_deposit_amount}"

@app.route('/deposit_rent_amount',methods=['POST'])
def deposit_rent_amount():
    
    login_id = session.get('login_id')

    deposit_amount_str = request.form['deposit_amount']
    deposit_amount = int(deposit_amount_str)
    py_mongodb_collection_customer.update_one({'Login id':login_id},{'$set':{'deposit_amount':deposit_amount}})
    
    customer_deposit_amount = py_mongodb_collection_customer.find_one({'Login id': login_id}, {'deposit_amount': 1, '_id': 0})

    # return customer_deposit_amount
    return f"Amount <strong>{customer_deposit_amount.get('deposit_amount','')}</strong> Is Deposited Successfully ."

@app.route('/due_rent_amount',methods=['POST'])
def due_rent_amount():
    login_id = session.get('login_id')

    due_amount=0

    customer_total_amount = py_mongodb_collection_customer.find_one({'Login id': login_id}, {'total_amount': 1, '_id': 0})
    total_amount_var = customer_total_amount.get('total_amount', 0)

    customer_deposit_amount = py_mongodb_collection_customer.find_one({'Login id': login_id}, {'deposit_amount': 1, '_id': 0})
    deposit_amount_var = customer_deposit_amount.get('deposit_amount', 0)

    due_amount = total_amount_var - deposit_amount_var

    py_mongodb_collection_customer.update_one({'Login id':login_id},{'$set':{'due_amount':due_amount}})

    customer_due_amount = py_mongodb_collection_customer.find_one({'Login id': login_id}, {'due_amount': 1, '_id': 0})

    
    return f"<strong>{customer_due_amount.get('due_amount','')}</strong> Is Due."
    # return customer_due_amount


@app.route('/add_vehicle',methods=['POST'])
def add_vehicle():
    login_id = session.get('login_id')

    new_vehicles = request.form.getlist('vehicle')

    new_vehicles_array = [{'vehicle': vehicle} for vehicle in new_vehicles]

    py_mongodb_collection_customer.update_one({'Login id': login_id}, {'$push': {'Vehicles': {'$each': new_vehicles_array}}})

    customer_details = py_mongodb_collection_customer.find_one({'Login id': login_id}, {'Vehicles': 1, '_id': 0})

    vehicles_list = customer_details.get('Vehicles', [])

    vehicle_types = [vehicle['vehicle'] for vehicle in vehicles_list]

    return f"<strong>Rented Vehicles Are: </strong><br> {vehicle_types}"



@app.route('/remove_vehicle',methods=['POST'])
def remove_vehicle():
    login_id = session.get('login_id')

    remove_vehicles = request.form.getlist('vehicle')

    py_mongodb_collection_customer.update_one({'Login id': login_id}, {'$pull': {'Vehicles': {'vehicle': {'$in': remove_vehicles}}}})


    customer_details = py_mongodb_collection_customer.find_one({'Login id': login_id}, {'Vehicles': 1, '_id': 0})

    vehicles_list = customer_details.get('Vehicles', [])

    vehicle_types = [vehicle['vehicle'] for vehicle in vehicles_list]

    return f"<strong>Rented Vehicles Are: </strong><br> {vehicle_types}"

@app.route('/update_hours',methods=['POST'])
def update_hours():
    login_id = session.get('login_id')
    update_hours_str = request.form['update_hours']

    update_hours = int(update_hours_str)

    py_mongodb_collection_customer.update_one({'Login id':login_id},{'$set':{'Hours':update_hours}})

    hours = py_mongodb_collection_customer.find_one({'Login id':login_id},{'Hours':1,"_id":0})



    # return f"Hours is updated by {hours}"
    return f"Hours Is Updated By <strong> {hours.get('Hours')}</strong>"


@app.route('/delete_details',methods=['POST'])
def delete_details():
    login_id = session.get('login_id')
    py_mongodb_collection_customer.delete_one({'Login id':login_id})
    return render_template('Login_page.html')

@app.route('/delete_acc',methods=['POST'])
def delete_acc():
    login_id = session.get('login_id')
    py_mongodb_collection_customer.delete_one({'Login id':login_id})
    py_mongodb_collection_login.delete_one({'login_id':login_id})
    return render_template('Sign_in_page.html')


@app.route('/view_vehicle',methods=['POST'])
def view_vehicle():
    
    login_id = session.get('login_id')
    pipeline = [
        {"$match": {"Login id": login_id}},
        {"$unwind": "$Vehicles"},
        {"$group": {"_id": "$Vehicles.vehicle", "count": {"$sum": 1}}},
    ]
    group_vehicle = list(py_mongodb_collection_customer.aggregate(pipeline))

    string = ""

    for vehicle in group_vehicle:
        string += f"<strong>{vehicle['_id']}: {vehicle['count']}</strong> <br>"

    return string


@app.route('/view_all_costumer',methods=['POST'])
def view_all_costumer():
    login_id = session.get('login_id')

    pipeline = [
        {"$group": {"_id": "$Login id", "due_amount": {"$sum": "$due_amount"}, "first_name": {"$first": "$First Name"}}},
        {"$sort": {"due_amount": -1}}
    ]

    customers = py_mongodb_collection_customer.aggregate(pipeline)

    customer_names = [customer['first_name'] for customer in customers]

    str1 = ", "

    

    return  f"<b>List Of Costumer Sorted By Due Amount</b> <br>" + str1.join(customer_names)
    

if __name__ == "__main__":
    app.run(debug=True)
    app_start()





# @app.route('/show_single_vehicle_details', methods=['POST'])
# def show_single_vehicle_details():
#     login_id = session.get('login_id')

#     customer_data = py_mongodb_collection_customer.find_one({'Login id': login_id}, {'Vehicles': 1, '_id': 0})

#     if customer_data:
#         vehicles = customer_data.get('Vehicles', [])

#         if len(vehicles) == 1:
#             first_name = customer_data.get('First Name', '')
#             last_name = customer_data.get('Last Name', '')
#             age = customer_data.get('Age', '')
#             licence = customer_data.get('Licence', '')
#             hours = customer_data.get('Hours', '')
#             vehicle_type = vehicles[0]['vehicle']

#             return print_single_vehicle_details(first_name, last_name, age, licence, hours, vehicle_type)
#         else:
#             return "<strong>User owns more than one vehicle. This method is only for users with a single vehicle.</strong>"
#     else:
#         return "<strong>Customer Data Not Found!!!</strong>"

# def print_single_vehicle_details(first_name, last_name, age, licence, hours, vehicle_type):
#     string = (
#         f"<strong>First Name:</strong> {first_name}<br><br>"
#         f"<strong>Last Name:</strong> {last_name}<br><br>"
#         f"<strong>Age:</strong> {age}<br><br>"
#         f"<strong>Licence:</strong> {licence}<br><br>"
#         f"<strong>Hours:</strong> {hours}<br><br>"
#         f"<strong>Vehicle:</strong> {vehicle_type}<br><br>"
#     )

#     return string
