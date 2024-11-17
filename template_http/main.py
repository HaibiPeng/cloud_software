import os
import tempfile    # To create temporary file before uploading to bucket
from google.cloud import storage
# Add any imports that you may need, but make sure to update requirements.txt
from flask import Flask, jsonify

app = Flask(__name__)

def create_text_file_http(request):
	# TODO: Add logic here
    bucketName = os.environ.get('BUCKET_ENV_VAR', 'Specified environment variable is not set.')
    # bucketName = 'bucket'

    request_json = request.get_json(silent=True)

    if request_json and 'fileName' in request_json:
        name = request_json['fileName']
    if request_json and 'fileContent' in request_json:
        content = request_json['fileContent']
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucketName)
    my_file = bucket.blob(name)
    with tempfile.NamedTemporaryFile('w+', prefix=name) as temp_file:
        temp_file.write(content)
        temp_file.flush()
        my_file.upload_from_filename(temp_file.name)
    data = {"fileName": name}
    return jsonify(data), 200