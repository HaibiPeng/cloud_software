import os
import json
import base64
from google.cloud import pubsub_v1
# Add any imports that you may need, but make sure to update requirements.txt

def restaurant_orders_pubsub(event, context):
    # TODO: Add logic here
    if 'data' in event:
        data = base64.b64decode(event['data']).decode('utf-8')
    order = json.loads(data)
    type = order['type']
    message_json = json.dumps(order)
    message_bytes = message_json.encode('utf-8')
    publisher = pubsub_v1.PublisherClient()
    if type == 'takeout':
        topic_path = publisher.topic_path('compelling-mesh-326115', 'restaurant_takeout_orders')
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result()  # Verify the publish succeeded
    elif type == 'eat-in':
        topic_path = publisher.topic_path('compelling-mesh-326115', 'restaurant_eat-in_orders')
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result()  # Verify the publish succeeded
    else:
        pass
