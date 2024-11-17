from flask import Flask, jsonify, request, Response
from database.db import initialize_db
from database.models import Photo, Album
import json
from bson.objectid import ObjectId
import os
import urllib
import base64
import codecs

app = Flask(__name__)

# configure the settings for the database
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://mongo:1048/flask-database'
}

# initialize the database
db = initialize_db(app)


# Helper functions to be used if required
def str_list_to_objectid(str_list):
    return list(
        map(
            lambda str_item: ObjectId(str_item),
            str_list
        )
    )


def object_list_as_id_list(obj_list):
    return list(
        map(
            lambda obj: str(obj.id),
            obj_list
        )
    )


# Album APIs
@app.route('/listAlbum', methods=["POST"])
def add_album():
    body = request.get_json()
    print(body)
    album = Album(**body).save()
    output = {'message': 'Album successfully created', 'id': str(album.id)}
    status_code = 201
    return jsonify(output), status_code


@app.route('/listAlbum/<album_id>', methods=['GET', 'PUT', 'DELETE'])
def operate_album_by_id(album_id):
    if request.method == 'GET':
        album = Album.objects.get_or_404(id=album_id)
        output = album
        status_code = 200
        return jsonify(output), status_code
        pass
    elif request.method == 'PUT':
        body = request.get_json()
        keys = body.keys()
        if body and keys:
            Album.objects.get_or_404(id=album_id).update(**body)
        output = {'message': 'Album successfully updated', 'id': str(album_id)}
        status_code = 200
        return jsonify(output), status_code
    elif request.method == "DELETE":
        album = Album.objects.get_or_404(id=album_id)
        album.delete()
        output = {'message': 'Album successfully deleted', 'id': str(album_id)}
        status_code = 200
        return jsonify(output), status_code


# Photo APIs
@app.route('/listPhoto', methods=["POST"])
def add_photo():
    posted_image = request.files['file']
    name = request.form.get('name')
    tags = request.form.getlist('tags')
    location = request.form.get('location')
    albums = request.form.getlist('albums')

    # Check for default album
    def_albums = Album.objects(name='Default')
    if not def_albums:
        pass
    photo = Photo(name=name, tags=tags, location=location, image_file=None, albums=albums)
    photo.image_file.replace(posted_image)
    photo.save()
    output = {'message': 'Photo successfully created', 'id': str(photo.id)}
    status_code = 201
    return jsonify(output), status_code


@app.route('/listPhoto/<photo_id>', methods=['GET', 'PUT', 'DELETE'])
def operate_photo_by_id(photo_id):
    if request.method == "GET":
        photo = Photo.objects.get_or_404(id=photo_id)
        if photo:
            # # Photos should be encoded with base64 and decoded using UTF-8 in all GET requests with an image before
            # sending the image as shown below
            base64_data = codecs.encode(photo.image_file.read(), 'base64')
            image = base64_data.decode('utf-8')
            output = {'name': photo.name, 'tags': photo.tags, 'location': photo.location,
                      'albums': object_list_as_id_list(photo.albums), 'file': image}
            status_code = 200
            return jsonify(output), status_code
    elif request.method == "PUT":
        photo = Photo.objects.get_or_404(id=photo_id)
        if photo:
            body = request.get_json()
            keys = body.keys()
            if body and keys:
                body["albums"] = str_list_to_objectid(body["albums"])
                photo.update(**body)
                output = {'message': 'Photo successfully updated', 'id': str(photo_id)}
                status_code = 200
                return jsonify(output), status_code
    elif request.method == "DELETE":
        photo = Photo.objects.get_or_404(id=photo_id)
        photo.delete()
        output = {'message': 'Photo successfully deleted', 'id': str(photo_id)}
        status_code = 200
        return jsonify(output), status_code


@app.route('/listPhotos', methods=['GET'])
def get_photos():
    name, value = request.query_string.decode().split('=')
    tag = value if name == "tag" else None
    albumName = value if name == "albumName" else None
    photo_objects = []
    if albumName is not None:
        for photo in Photo.objects:
            albums = object_list_as_id_list(photo.albums)
            albumNames = [Album.objects.get(id=album_id).name for album_id in albums]
            if albumName in albumNames:
                photo_objects.append(photo)
        pass
    elif tag is not None:
        for photo in Photo.objects:
            if tag in photo.tags:
                photo_objects.append(photo)
        pass
    else:
        pass
    photos = []
    for photo in photo_objects:
        base64_data = codecs.encode(photo.image_file.read(), 'base64')
        image = base64_data.decode('utf-8')
        photos.append({'name': photo.name, 'location': photo.location, 'file': image})
    return jsonify(photos), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
