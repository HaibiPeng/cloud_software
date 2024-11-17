from types import SimpleNamespace

import pika
import json
import dateutil.parser
import time
from db_and_event_definitions import customers_database, cost_per_unit, number_of_units, BillingEvent, ProductEvent
from xprint import xprint

class ShoppingWorker:

    def __init__(self, worker_id, queue, weight="1"):
        # Do not edit the init method.
        # Set the variables appropriately in the methods below.
        self.connection = None
        self.channel = None
        self.worker_id = worker_id
        self.queue = queue
        self.weight = weight
        self.shopping_state = {}
        self.shopping_events = []
        self.billing_event_producer = None
        self.customer_app_event_producer = None

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMQ connection, channel, exchange and queue here
        # Also initialize the channels for the billing_event_producer and customer_app_event_producer
        xprint("ShoppingWorker {}: initialize_rabbitmq() called".format(self.worker_id))
        # credentials = pika.PlainCredentials(
        #     username="user", password="password")
        # self.connection = pika.BlockingConnection(
        #     pika.ConnectionParameters(host="0.0.0.0",
        #                               port=8080,
        #                               virtual_host="/",
        #                               socket_timeout=15,
        #                               credentials=credentials))
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        self.channel = self.connection.channel()
        # topic exchange: route messages to one or many queues based on matching between a message routing key 
        # and the pattern that was used to bind a queue to an exchange
        # often used to implement various publish/subscribe pattern variations
        self.channel.exchange_declare(exchange="customer_app_events", exchange_type="topic")

        self.channel.queue_declare(queue=self.queue)
        # Purge all of the messages from the specified queue
        self.channel.queue_purge(queue=self.queue)
        # Bind the queue to the specified exchange
        self.channel.queue_bind(exchange="shopping_events_exchange", queue=self.queue, routing_key=self.weight)
        # Consume to the broker and binds messages for the consumer_tag to the consumer callback
        self.channel.basic_consume(on_message_callback=self.handle_shopping_event, queue=self.queue, auto_ack=True)
        
        self.billing_event_producer = BillingEventProducer(self.connection, self.worker_id)
        self.billing_event_producer.initialize_rabbitmq()

        self.customer_app_event_producer = CustomerEventProducer(self.connection, self.worker_id)
        self.customer_app_event_producer.initialize_rabbitmq()


    def handle_shopping_event(self, ch, method, properties, body):
        # To implement - This is the callback that is passed to "on_message_callback" when a message is received
        xprint("ShoppingWorker {}: handle_event() called".format(self.worker_id))
        # Handle the application logic and the publishing of events here
        json2python = json.loads(body)
        productEvent = ProductEvent(event_type=json2python["event_type"], product_number=json2python["product_number"],
                                 timestamp=json2python["timestamp"])
        
        bad_message = json.dumps(vars(productEvent))
        product_numbers = customers_database.values()
        if productEvent.product_number in product_numbers:
            self.shopping_events.append(productEvent)
        else:
            # negatively acknowledged messages are republished by the RabbitMQ Broker to a dead letter queue
            self.channel.queue_declare(queue="shopping_events_dead_letter_queue",
                                       arguments={
                                           "x-dead-letter-exchange": "",
                                           "x-dead-letter-routing-key": "shopping_events_dead_letter_queue"
                                       })

            self.channel.basic_publish(exchange="",
                                       routing_key="shopping_events_dead_letter_queue",
                                       body=bad_message)
        
        customer_id = self.get_customer_id_from_shopping_event(productEvent)
        self.customer_app_event_producer.publish_shopping_event(customer_id, productEvent)
        if customer_id == None:
            pass
        if productEvent.event_type == "pick up":
            self.shopping_state[productEvent.product_number] = productEvent.timestamp
            xprint(self.shopping_state)
        elif productEvent.event_type == "purchase":
            xprint(self.shopping_state)
            pickupEvent = self.shopping_state[productEvent.product_number]
            self.shopping_state.pop(productEvent.product_number)
            if pickupEvent == None:
                xprint("no such product:" + str(customer_id))
                return
            pickup_time = pickupEvent
            purchase_time = productEvent.timestamp
            shopping_cost = cost_per_unit * number_of_units * 0.8

            billingEvent = BillingEvent(customer_id=customer_id, product_number=productEvent.product_number,
                                        pickup_time=pickup_time, purchase_time=purchase_time,
                                        shopping_cost=shopping_cost)

            self.channel.queue_declare(queue="billing_events")

            self.customer_app_event_producer.publish_billing_event(billingEvent)
            self.billing_event_producer.publish(billingEvent)

    # Utility function to get the customer_id from a shopping event
    def get_customer_id_from_shopping_event(self, shopping_event):
        customer_id = [customer_id for customer_id, product_number in customers_database.items()
                       if shopping_event.product_number == product_number]
        if len(customer_id) == 0:
            xprint("{}: Customer Id for product number {} Not found".format(self.worker_id, shopping_event.product_number))
            return None
        return customer_id[0]

    def start_consuming(self):
        # To implement - Start consuming from Rabbit
        xprint("ShoppingWorker {}: start_consuming() called".format(self.worker_id))
        self.channel.start_consuming()

    def close(self):
        # Do not edit this method
        try:
            xprint("Closing worker with id = {}".format(self.worker_id))
            self.channel.stop_consuming()
            time.sleep(1)
            self.channel.close()
            self.billing_event_producer.close()
            self.customer_app_event_producer.close()
            time.sleep(1)
            self.connection.close()
        except Exception as e:
            print("Exception {} when closing worker with id = {}".format(e, self.worker_id))


class BillingEventProducer:

    def __init__(self, connection, worker_id):
        # Do not edit the init method.
        self.worker_id = worker_id
        # Reusing connection created in ShoppingWorker
        self.channel = connection.channel()

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        xprint("BillingEventProducer {}: initialize_rabbitmq() called".format(self.worker_id))
        self.channel.queue_declare(queue="billing_events")

    def publish(self, billing_event):
        xprint("BillingEventProducer {}: Publishing billing event {}".format(
            self.worker_id,
            vars(billing_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(billing_event)) to convert the shopping_event object to JSON
        message = json.dumps(vars(billing_event))
        self.channel.basic_publish(exchange="", routing_key="billing_events", body=message)

    def close(self):
        # Do not edit this method
        self.channel.close()


class CustomerEventProducer:

    def __init__(self, connection, worker_id):
        # Do not edit the init method.
        self.worker_id = worker_id
        # Reusing connection created in ShoppingWorker
        self.channel = connection.channel()

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        xprint("CustomerEventProducer {}: initialize_rabbitmq() called".format(self.worker_id))
        self.channel.exchange_declare(exchange="customer_app_events", exchange_type="topic")

    def publish_billing_event(self, billing_event):
        xprint("{}: CustomerEventProducer: Publishing billing event {}"
              .format(self.worker_id, vars(billing_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(billing_event)) to convert the shopping_event object to JSON
        message = json.dumps(vars(billing_event))
        self.channel.basic_publish(exchange="customer_app_events", routing_key=billing_event.customer_id, body=message)

    def publish_shopping_event(self, customer_id, shopping_event):
        xprint("{}: CustomerEventProducer: Publishing shopping event {} {}"
              .format(self.worker_id, customer_id, vars(shopping_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(shopping_event)) to convert the shopping_event object to JSON
        message = json.dumps(vars(shopping_event))
        self.channel.basic_publish(exchange="customer_app_events", routing_key=customer_id, body=message)

    def close(self):
        # Do not edit this method
        self.channel.close()
