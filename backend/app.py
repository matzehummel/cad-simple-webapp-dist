import os
from urllib import response

from flask import Flask, make_response, request, url_for, redirect
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
import jsonpickle
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'serviceAccountKey.json'

storage_client = storage.Client()

bucket = storage_client.get_bucket("cadwebappscards")
bucket.iam_configuration.uniform_bucket_level_access_enabled = False
bucket.patch()


UPLOAD_FOLDER = 'C:/Projects/Masterstudium/CAD/cad-exercise/python_backend/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#app.config.update(
#    GOOGLE_STORAGE_LOCAL_DEST = app.instance_path,
#    GOOGLE_STORAGE_SIGNATURE = {"expiration": timedelta(minutes=5)},
#    GOOGLE_STORAGE_FILES_BUCKET = "cad-webapp-cards"
#)
#storage.init_app(app)

client = MongoClient('localhost', 27017)

db = client.caddb
cards = db.cards
print(db.name)

cors = CORS(app)


content = []

@app.route("/allCards", methods=['GET'])
@cross_origin()
def getCards():
    cursor = cards.find({})
    response = []
    for record in cursor:
        newCard = {}
        newCard["title"] = record["title"]
        try:
            newCard["imageUrl"] = record["imageUrl"]
            print(newCard["imageUrl"])
        except:
            print("no Image URL")
        newCard["tags"] = record["tags"]
        response.append(newCard)
    return make_response(jsonpickle.dumps(response, unpicklable=False, keys=False))

@app.route("/cardsByTags", methods=['GET'])
@cross_origin()
def getCardsByTags():
    title = request.args.get('tags')
    record = cards.find_one({'title': title})
    newCard = {}
    response = []
    if record is not None:
        newCard["title"] = record["title"]
        try:
            newCard["imageUrl"] = record["imageUrl"]
            print(newCard["imageUrl"])
        except:
            print("no Image URL")
        newCard["tags"] = record["tags"]
        response = [newCard]
    return make_response(jsonpickle.dumps(response, unpicklable=False, keys=False))


@app.route("/upload_image", methods=['POST'])
@cross_origin()
def upload_image():
    imageFile = request.files["image"]
    blob = bucket.blob("images/" + imageFile.filename)
    blob.upload_from_file(imageFile)
    publicUrl = blob.public_url
    return publicUrl

@app.route("/card", methods=['POST'])
@cross_origin()
def add():
    title = request.json['title']
    newImageUrl = request.json['imageUrl']
    tags = request.json['tags']
    cards.insert_one({'title': title, 'imageUrl': newImageUrl, 'tags': tags})
    
    return redirect(url_for('getCards'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")