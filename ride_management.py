from Models.Driver import Driver
from Models.Location import Location
from flask import Blueprint, jsonify, json, request, session, current_app
from db_handler import load_firebase_credential

ride_app = Blueprint('ride-management', __name__)


@ride_app.route('/api/add/driver/details', methods=['POST'])
def add_ride():
    try:
        add_driver = json.loads(request.data)
        driver = Driver(session.get('login_name'), session.get('login_email'), session.get('contact'),
                        add_driver['vehicle'])
        loc = Location(add_driver['from'], add_driver['to'])
        data = {
            "driver": driver.dict(),
            "location": loc.dict(),
            "date": add_driver['date'],
            "time": add_driver['time'],
            "fare": add_driver['fare']
        }
        print("Data:", data)
        db = load_firebase_credential()
        collection_name = current_app.config.get('AVAILABLE_DRIVERS')
        db.collection(collection_name).add(data)
        return jsonify(message=True)
    except Exception as e:
        print(str(e))
        return jsonify(message=False)
