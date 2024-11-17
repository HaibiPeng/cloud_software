import json

import pika

from xprint import xprint


class ShoppingEventProducer:

    def __init__(self):
        # Do not edit the init method.
        # Set the variables appropriately in the methods below.
        self.connection = None
        self.channel = None

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        xprint("ShoppingEventProducer initialize_rabbitmq() called")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        self.channel = self.connection.channel()
        # creates an exchange if it does not already exist
        # durable (bool) – Survive a reboot of RabbitMQ
        self.channel.exchange_declare(exchange="shopping_events_exchange",
                                      exchange_type="x-consistent-hash",
                                      durable=True)

    def publish(self, shopping_event):
        xprint("ShoppingEventProducer: Publishing shopping event {}".format(vars(shopping_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(shopping_event)) to convert the shopping_event object to JSON
        message = json.dumps(vars(shopping_event))
        # Publish to the channel with the given exchange, routing key and body
        # routing_key (str) – The routing key to bind on; specify exactly to which queue the message should go
        self.channel.basic_publish(exchange="shopping_events_exchange",
                                   routing_key=shopping_event.product_number,
                                   body=message)

    def close(self):
        # Do not edit this method
        self.channel.close()
        self.connection.close()
