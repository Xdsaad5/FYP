from geopy.geocoders import Nominatim
from Models.Driver import Driver
from Models.Location import Location
from flask import Blueprint, jsonify, json, request, session, current_app
from db_handler import load_firebase_credential
from datetime import datetime

ride_app = Blueprint('ride-management', __name__)


def geocode_location(location_name):
    try:
        geolocator = Nominatim(user_agent="geocode_function", timeout=5)
        location = geolocator.geocode(location_name)
        if location:
            return location.latitude, location.longitude  # Return as tuple
        else:
            return None
    except Exception as e:
        print(str(e))


@ride_app.route('/api/add/driver/details', methods=['POST'])
def add_driver():
    try:
        ride_details = json.loads(request.data)
        # as the driver is the person who is current login in our website, so we get his info from session
        driver = Driver(session.get('login_name'), session.get('login_email'), session.get('contact'),
                        ride_details['vehicle'])
        loc = Location(ride_details['start'], ride_details['end'])
        if not geocode_location(loc.stat_loc):
            return jsonify(message='Enter valid Start Location.')
        if not geocode_location(loc.end_loc):
            return jsonify(message='Enter valid End Location.')
        data = {
            "driver": driver.dict(),
            "location": loc.dict(),
            "date": ride_details['date'],
            "time": ride_details['time'],
            "fare": ride_details['fare'],
            "available_seats": driver.total_seats
        }
        # print("Data:", data)
        db = load_firebase_credential()
        collection_name = current_app.config.get('AVAILABLE_DRIVERS')
        db.collection(collection_name).add(data)
        return jsonify(message=True)
    except Exception as e:
        print(str(e))
        return jsonify(message=False)


def enrolled_communities(email):
    try:
        collection_name = current_app.config.get('JOIN_COMMUNITIES_COLLECTION')
        db = load_firebase_credential()
        query = db.collection(collection_name).where('email', '==', email)
        result = query.get()
        joined_communities = []
        for data in result:
            data = data.to_dict()
            joined_communities.append(data.get('community_name'))
        return joined_communities
    except Exception as e:
        print(str(e))
        return jsonify(message=False)


def get_community_members(joined_communities, current_user):
    try:
        db = load_firebase_credential()
        members = set()
        # Fetch members for each community in joined_communities
        collection_name = current_app.config.get('JOIN_COMMUNITIES_COLLECTION')
        for community_name in joined_communities:
            query = db.collection(collection_name).where("community_name", "==", community_name)
            result = query.get()
            for doc in result:
                data = doc.to_dict()
                if data.get('email') != current_user:
                    members.add(data.get('email'))
        return members
    except Exception as e:
        print(str(e))
        return []


def available_drivers(community_members):
    try:
        current_date = datetime.now()
        # Fetch all drivers
        db = load_firebase_credential()
        collection_name = current_app.config.get('AVAILABLE_DRIVERS')
        drivers_collection = db.collection(collection_name)
        drivers_query = drivers_collection.get()
        # Prepare response
        drivers_data = []
        for driver in drivers_query:
            driver_data = driver.to_dict()
            # Convert string date to datetime object
            driver_date = datetime.strptime(driver_data.get("date"), "%d/%m/%Y")
            # Filter drivers whose email matches with community members and schedule date is greater than current date
            if ((driver_data.get("driver", {}).get("email") in community_members)
                    and (driver_date > current_date) and int(driver_data.get('available_seats')) > 0):
                driver_data.update(id=driver.id)
                drivers_data.append(driver_data)
        return drivers_data
    except Exception as e:
        print(str(e))
        return []


'''
In this feature  we have to list only those drivers which is member of that community in which user also added 
we will do the following task to achieve above functionality,
1-we need to find in which communities user is added. for this we use (enrolled_communities) function
2-we need to find the members of that communities in which user currently added,for this we use 
(get_community_members)function
3-After getting member we will see if any of the member schedule any ride for this we use (available_drivers) function
'''


@ride_app.route('/api/search/ride')
def search_ride():
    try:
        current_user = session.get('login_email')
        joined_communities = enrolled_communities(current_user)
        if not joined_communities:
            return jsonify(message='Please Join community to start ride.')
        community_members = get_community_members(joined_communities, current_user)
        # print(community_members)
        drivers = available_drivers(community_members)
        # print(drivers)
        if not drivers:
            return jsonify(message='No Driver Available to book ride.')
        return jsonify(message=drivers)
    except Exception as e:
        print(str(e))
        return jsonify(message=False)


def update_driver_information(driver_id, increment=True):
    try:
        db = load_firebase_credential()
        collection_name = current_app.config.get('AVAILABLE_DRIVERS')
        driver_ref = db.collection(collection_name).document(driver_id)

        # getting document
        driver_doc = driver_ref.get()
        if not driver_doc.exists:
            return jsonify(message='Driver not found')

        # getting  available seats and update
        current_seats = driver_doc.get('available_seats')
        print(f'current_seats: {current_seats}')
        if increment:
            driver_ref.update({'available_seats': current_seats + 1})
            return True

        if current_seats <= 0:
            return False

        # update the document
        driver_ref.update({'available_seats': current_seats - 1})

        return True

    except Exception as e:
        print(str(e))
        return False


def add_ride(driver_id):
    try:
        db = load_firebase_credential()
        collection_name = current_app.config.get('BOOKED_RIDES')
        ref = db.collection(collection_name)
        print(driver_id)
        data = {
            'driver_id': driver_id,
            'passenger_email': session.get('login_email')
        }
        ref.add(data)
        return True
    except Exception as e:
        print(str(e))
        return False


'''
In book_ride feature the user can select a ride which we list using function search_ride,
in this feature we get driver_id to uniquely identify which driver user selected, after
that we update available seats of driver vehicle using function update_driver_information
after updating information of driver we use function add_ride to add driver_id and passenger 
email in database collection
'''


@ride_app.route('/api/book/ride', methods=['POST'])
def book_ride():
    try:
        data = json.loads(request.data)
        driver_id = data.get('id')
        if not update_driver_information(driver_id, False):
            return jsonify(message="No seats available.")
        if not add_ride(driver_id):
            return jsonify(message="Error in your details.")
        return jsonify(message="Ride Book Successfully.")
    except Exception as e:
        print(str(e))
        return jsonify(message="Error in Booking your Ride.")


def driver_information(drivers):
    try:
        collection_name = current_app.config.get('AVAILABLE_DRIVERS')
        driver_info = []
        db = load_firebase_credential()
        for driver_id in drivers:
            driver_ref = db.collection(collection_name).document(driver_id).get()
            data = driver_ref.to_dict()
            temp = {
                'id': driver_id, 'name': data['driver']['name'], 'start': data['location']['start'],
                'end': data['location']['end'], 'date': data['date'], 'time': data['time']
            }
            driver_info.append(temp)
        return driver_info
    except Exception as e:
        print(str(e))


'''
in  passenger ride feature we return all the rides where current user act as passenger
or we can say where he book ride in this feature we use function driver_information(where
user act as a driver) to get his information
'''


@ride_app.route('/api/passenger/rides')
def passenger_rides():
    try:
        db = load_firebase_credential()
        collection_name = current_app.config.get('BOOKED_RIDES')
        query = db.collection(collection_name).where('passenger_email', '==', session.get('login_email'))
        query_result = query.get()
        result_list = [doc.to_dict()['driver_id'] for doc in query_result]
        if not result_list:
            return jsonify(message="No Ride Schedule.")
        drivers = driver_information(result_list)
        return jsonify(message=drivers)
    except Exception as e:
        print(str(e))
        return jsonify(message="No Ride Schedule.")


'''
in this feature we cancel ride by passenger by getting information of driver's id
'''


@ride_app.route('/api/cancel/ride/by/passenger', methods=['POST'])
def cancel_ride_by_passenger():
    try:
        data = json.loads(request.data)
        driver_id = data.get('id')
        update_driver_information(driver_id)
        collection_name = current_app.config.get('BOOKED_RIDES')
        db = load_firebase_credential()
        query = (db.collection(collection_name)
                 .where('passenger_email', '==', session.get('login_email')).where('driver_id', '==', driver_id))
        doc = query.get()
        # Check if the document exists
        if not doc:
            return jsonify(message="No Ride Schedule")
        doc[0].reference.delete()
        return jsonify(message='Your ride has been canceled.')
    except Exception as e:
        print(str(e))
        return jsonify(message="No Ride Schedule.")


'''
in  driver ride feature we return all the rides where current user act as driver
'''


@ride_app.route('/api/driver/rides')
def driver_rides():
    try:
        db = load_firebase_credential()
        collection_name = current_app.config.get('AVAILABLE_DRIVERS')
        driver_email = session.get('login_email')

        # Query drivers where the driver's email matches the logged-in user's email
        query = db.collection(collection_name).where('driver.email', '==', driver_email)
        query_result = query.get()
        driver_ride = []
        for doc in query_result:
            data = doc.to_dict()
            driver_id = doc.id
            temp = {
                "id": driver_id,
                "name": data['driver']['name'], "start": data['location']['start'],
                "end": data['location']['end'], "date": data['date'], "time": data['time'],
            }
            driver_ride.append(temp)
        if not driver_ride:
            return jsonify(message="No Ride Schedule.")
        return jsonify(message=driver_ride)
    except Exception as e:
        print(str(e))
        return jsonify(message="No Ride Schedule.")
