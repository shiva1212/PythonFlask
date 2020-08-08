from flask import (Flask, jsonify, request, render_template)
from flask_pymongo import PyMongo
import json

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
mongo = PyMongo(app)


# stores = [
#     {
#         "name": "Indain Grocery Market",
#         "items": [
#             {
#                 "name": "My Item1",
#                 "Price": 12.99
#             },
#             {
#                 "name": "My Item2",
#                 "Price": 12.99
#             }
#         ]
#     }
# ]


@app.route("/")
def home():
    return render_template('index.html')


# post /store data: {name:}

@app.route("/store", methods=["POST"])
def create_store():
    request_data = request.get_json()
    #if next(filter(lambda x: x['name'] == request_data["name"], mongo), None):
        #return {'message': "An item with name '{}' already exists." .format(request_data["name"])}
    store_id = mongo.db.store.insert_one(request_data)


    return jsonify({"name": request_data["name"], "message": "store is created successfully" },201 if request_data else  404)


@app.route("/store/<string:name>")
def get_store(name):
    store = mongo.db.store.find_one({"name": name})
    if store:
        del store["_id"]
        return jsonify(store)
    return jsonify({'message': 'store not found'})


@app.route("/store/<string:name>", methods=["DELETE"])
def delete_store(name):
    store = mongo.db.store.delete_one({"name": name})
    if store:
        return jsonify({'message': 'Deleted Successfully'})
    else:
        return jsonify({'message': 'Does not Exist'})


@app.route("/store/<string:name>", methods=["PUT"])
def update_store(name):
    request_data = request.get_json()
    store = mongo.db.store.update({"name": name}, {"$set": request_data})
    if store:
        return jsonify({"message": "Store Updated Successfully"})
    else:
        return jsonify({'message': 'store did not updated successfully'})


# GET /store
@app.route("/store")
def getStores():
    mongo_data = mongo.db.store.find({})
    stores = []
    for data in mongo_data:
        del data["_id"]
        stores.append(data)
    return jsonify({"stores": stores})


# POST /store/<string:name>/item {name:, price:}
# @app.route("/store/<string:name>/item", methods=["POST"])
# def create_item_in_store(name):
#     request_data = request.get_json()
#     for store in stores:
#         if store["name"] == name:
#             new_item = {
#                 "name": request_data["name"],
#                 "price": request_data["price"]
#             }
#             store["item"].append(new_item)
#             return jsonify(new_item)
#     return jsonify({"message": "Store not found"})


# GET /store/<string:name>/item
# @app.route("/store/<string:name>/item")
# def get_items_in_store(name):
#     for store in stores:
#         if store["name"] == name:
#             return jsonify({"items": store["items"]})
#     return jsonify({"message": "items not found"})


if __name__ == "__main__":
    app.run(port=3000)
