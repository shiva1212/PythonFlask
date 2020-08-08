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
ns = api.namespace('stores', description='CRUD Operations')  # for different modules nameSpace should be different

ITEM_MODEL = ns.model("item", model={
    "name": fields.String(max_length=50, required=True),
    "price": fields.Float(required=True),

})

STORE_MODEL = ns.model("store", model={
    "id": fields.Integer(required=True),
    "name": fields.String(max_length=50, required=True, min_length=10),
    "items": fields.List(fields.Nested(model=ITEM_MODEL), required=True)
})
GENRIC_MODEL = ns.model("genric", model={
    "id": fields.Integer(),
    "message": fields.String()
})

@ns.route('')
class StoreList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('Get List of Stores')
    @ns.marshal_list_with(STORE_MODEL, code=200)
    def get(self):
        '''List all stores'''
        mongo_data = mongo.db.store.find({})
        stores = []
        for data in mongo_data:
            del data["_id"]
            stores.append(data)
        return stores, 200

    @ns.doc('create_store')
    @ns.expect(STORE_MODEL)
    @ns.marshal_with(GENRIC_MODEL)
    @ns.response(409, "Id already exists")
    def post(self):
        '''Create a new task'''
        request_data = request.get_json()
        stores = mongo.db.store.find({"$or": [{"id": request_data.get("id")}, {"name": request_data.get("name")}]})
        for store in stores:
            app.logger.info("ID already exist. Try with another id")
            abort(409, "Id already exist")

        store_id = mongo.db.store.insert_one(request_data)
        return {"id": request_data.get("id"), "message": "Store is ceated successfully"}, 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class StoreDetail(Resource):

    @ns.doc('get_todo')
    @ns.marshal_with(STORE_MODEL)
    def get(self, id):
        '''Fetch a given store detail'''
        store = mongo.db.store.find_one({"id":id}, {"_id": 0})
        if store:
            return store, 200
        else:
            abort(404,"Store not found")
            # raise CustomException(data={"message":"Store not found"}, message_code="NOT_FOUND", status=HTTPStatus.NOT_FOUND)




    @ns.doc('delete_store')
    # @ns.response(204, 'store deleted')
    @ns.marshal_with(GENRIC_MODEL)
    def delete(self, id):
        '''Delete a task given its identifier'''
        store = mongo.db.store.delete_one({"id": id})

        return {"id": id, "message": "Store is deleted successfully"}, 200

    @ns.expect(STORE_MODEL)
    @ns.marshal_with(GENRIC_MODEL)
    def put(self, id):
        '''Update a task given its identifier'''
        request_data = request.get_json()
        store = mongo.db.store.update({"id": id},{"$set": request_data})
        if store.get("updatedExisting"):
            return {"id": id, "message": "Store Updated Successfully"}, 202
        else:
            return {"id": id, 'message': 'store did not updated successfully'}, 404


if __name__ == '__main__':
    app.run(debug=True)
