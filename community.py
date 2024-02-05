import json
from flask import Blueprint, jsonify, request,current_app
from authentication import search_user
from db_handler import loadFirebaseCredential
community_blueprint = Blueprint('community', __name__)
def create_community(comm_info):
    try:
        db = loadFirebaseCredential()
        if not db:
            return jsonify(message="Error in creating community.")
        # community is our collection in firestore
        comm_ref = db.collection(current_app.config.get('COMMUNITY_COLLECTION'))
        # add the community data to Firestore
        community_data = {
            'name': comm_info['name'],
            'description': comm_info['description'],
            'code': comm_info['code'],
        }
        # add the document to the 'community' collection
        comm_ref.add(community_data)
        return jsonify(message="User successfully stored in Firestore")
    except Exception as e:
        return jsonify(Error=str(e))
@community_blueprint.route('/createCommunity', methods=['POST'])
def community_already_exist():
    community_info = json.loads(request.data)
    if not community_info:                                              #check if community(object) is null
        return jsonify(Error="Provided Community information isn't completed.")
    status = search_user('name',community_info['name'],current_app.config.get('COMMUNITY_COLLECTION'))              #check whether community already exist or not?
    if status > 0:
        return jsonify(message="Community already exist.")
    create_community(community_info)
    return jsonify(message="Community Successfully  created.")

