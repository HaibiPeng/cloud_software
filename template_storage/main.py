import os
import io # To read from saved file
from google.cloud import storage, vision
# Add any imports that you may need, but make sure to update requirements.txt
import tempfile

def detect_text(path):
    """Detects text in the file."""
    client_options = {'api_endpoint': 'eu-vision.googleapis.com'}
    client = vision.ImageAnnotatorClient(client_options=client_options)

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    return texts[0].description

def image_to_text_storage(data, context):
    # TODO: Add logic here
    bucket_name = data['bucket']
    image_name = data['name'].split('/')[-1]
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(image_name)
    blob.download_to_filename('/tmp/' + image_name)
    texts = detect_text('/tmp/' + image_name)
    txt_file = bucket.blob(image_name[0:-4] + '.txt')
    with tempfile.NamedTemporaryFile('w+', prefix=image_name[0:-4], suffix='.txt') as temp_file:
        temp_file.write(texts)
        temp_file.flush()
        txt_file.upload_from_filename(temp_file.name)