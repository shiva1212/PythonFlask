from http import HTTPStatus
from flask import Flask, request
from flask_pymongo import PyMongo
from flask_restx import Api, Resource, fields
from werkzeug.exceptions import abort

# from first_Flask.base_resource import BaseResource
# from first_Flask.custom_exception import CustomException
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
mongo = PyMongo(app)

api = Api(app, version="1.0", title="restXDemo",
          description="Learning for First Time")

ns = api.namespace('logins', description='CRUD Operations')

LOGIN_MODEL = ns.model("login", model = {
    "id": fields.Integer(required = True),
    "name": fields.String(max_length = 50, required = True),
    "email": fields.String(required = True),
    "password": fields.String(min_length = 8, required = True),
    "confirmpassword": fields.String(min_length = 8, required = True)
})


GENRIC_MODEL = ns.model("genric", model={
    "id": fields.Integer(),
    "message": fields.String()
})

@ns.route('')
class LoginList(Resource):
    
    @ns.doc("get list of login")
    @ns.marshal_list_with(LOGIN_MODEL, code = 200)
    def get(self):
        mongo_data = mongo.db.login.find({})
        logins = []
        for data in mongo_data:
            del data["_id"]
            logins.append(data)
        return logins, 200

    @ns.doc("Post data login")
    @ns.expect(LOGIN_MODEL)
    @ns.marshal_with(GENRIC_MODEL)
    @ns.response(409, "Id already exists")
    def post(self):
        request_data = request.get_json()
        logins = mongo.db.login.find({"$or": [{"id": request_data.get("id")}, {"name": request_data.get("name")}]})
        for login in logins:
            app.logger.info("ID already Exists. Try With another Id")
            abort(409, "Id already exist")
        
        store_id = mongo.db.login.insert_one(request_data)
        return {"id":request_data.get("id"), "message": "Store is ceated successfully"} , 201

@ns.route('/<int:id>')
@ns.response(404, 'Login not found')
@ns.param('id', 'The task identifier')
class LoginDetails(Resource):

    @ns.doc("Single Login Record")
    @ns.marshal_with(LOGIN_MODEL)
    def get_login(self, id):
        '''Fetch a given login detail'''
        login_id = mongo.db.login.find_one({"id": id},{"_id":0})
        if login_id:
            return login_id, 200
        else:
            abort(404, "Did not find detail")

    @ns.doc("delete login record")
    @ns.marshal_with(GENRIC_MODEL)
    def delete(self, id):
        
        delete_login = mongo.db.login.delete_one({"id":id})
        return {"id": id, "message": "Login Deleted Successfully"} , 200

    @ns.doc("Update Existing Record")
    @ns.expect(LOGIN_MODEL)
    @ns.marshal_with(GENRIC_MODEL)
    def put(self, id):
        
        request_data = request.get_json()
        update_login = mongo.db.login.update({"id": id},{"$set": request_data})
        if update_login.get("updatedExisting"):
            return {"id": id, "message": "login updated successfully"}, 202
        else:
            return {"id": id , "message": "login did not updated successfully"}, 404

if __name__ == '__main__':
    app.run(debug=True)