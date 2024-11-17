from types import SimpleNamespace
import pika
import json
from db_and_event_definitions import ParkingEvent, BillingEvent
import time
import logging

from xprint import xprint


class CustomerEventConsumer:

    def __init__(self, customer_id):
        # Do not edit the init method.
        # Set the variables appropriately in the methods below.
        self.customer_id = customer_id
        self.connection = None
        self.channel = None
        self.temporary_queue_name = None
        self.parking_events = []
        self.billing_events = []

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='customer_app_events', exchange_type="topic")

        result = self.channel.queue_declare('', exclusive=True)
        self.temporary_queue_name = result.method.queue
        self.channel.queue_bind(exchange="customer_app_events",
                                queue=self.temporary_queue_name,
                                routing_key=self.customer_id)

        # self.channel.queue_declare("billing_events")
        # self.channel.queue_bind(exchange="",
        #                         queue="billing_events",
        #                         routing_key=self.customer_id)

        # result = self.channel.queue_declare(queue="parking_events_exchange")
        # self.temporary_queue_name = result.method.queue
        # self.temporary_queue_name = result.method.queue

        # self.channel.queue_declare(queue="parking_events_exchange")
        # self.parking_events.append(ParkingEvent)
        # self.billing_events.append(BillingEvent)
        xprint("CustomerEventConsumer {}: initialize_rabbitmq() called".format(self.customer_id))

    def handle_event(self, ch, method, properties, body):
        xprint(" [x] Received %r" % body)
        # To implement - This is the callback that is passed to "on_message_callback" when a message is received
        xprint("CustomerEventConsumer {}: handle_event() called".format(self.customer_id))
        # def callback(ch, method, properties, body):
        json2python = json.loads(body)
        if 'event_type' in json2python:
            parkEvent = ParkingEvent(event_type=json2python['event_type'], car_number=json2python['car_number'],
                                     timestamp=json2python['timestamp'])
            self.parking_events.append(parkEvent)
        if 'customer_id' in json2python:
            billingEvent = BillingEvent(customer_id=json2python['customer_id'], car_number=json2python['car_number'],
                                        entry_time=json2python['entry_time'], exit_time=json2python['exit_time'],
                                        parking_cost=json2python['parking_cost'])
            self.billing_events.append(billingEvent)



    def start_consuming(self):
        # To implement - Start consuming from Rabbit
        self.channel.basic_consume(queue=self.temporary_queue_name,
                                   on_message_callback=self.handle_event,
                                   auto_ack=True)

        # self.channel.basic_consume(queue="billing_events",
        #                            on_message_callback=self.handle_event,
        #                            auto_ack=True)
        xprint("CustomerEventConsumer {}: start_consuming() called".format(self.customer_id))
        self.channel.start_consuming()

    def close(self):
        # Do not edit this method
        try:
            if self.channel is not None:
                print("CustomerEventConsumer {}: Closing".format(self.customer_id))
                self.channel.stop_consuming()
                time.sleep(1)
                self.channel.close()
            if self.connection is not None:
                self.connection.close()
        except Exception as e:
            print("CustomerEventConsumer {}: Exception {} on close()"
                  .format(self.customer_id, e))
            pass
