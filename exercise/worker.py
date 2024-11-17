from types import SimpleNamespace
import datetime
import pika
import json
import math
import dateutil.parser
import time
from db_and_event_definitions import customers_database, cost_per_hour, BillingEvent, ParkingEvent
from xprint import xprint


class ParkingWorker:

    def __init__(self, worker_id, queue, weight="1"):
        # Do not edit the init method.
        # Set the variables appropriately in the methods below.
        self.connection = None
        self.channel = None
        self.worker_id = worker_id
        self.queue = queue
        self.weight = weight
        self.parking_state = {}
        self.parking_events = []
        self.billing_event_producer = None
        self.customer_app_event_producer = None

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMQ connection, channel, exchange and queue here
        # Also initialize the channels for the billing_event_producer and customer_app_event_producer

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        # self.channel.exchange_declare(
        #     exchange='parking_events_exchange', exchange_tFype="x-consistent-hash", durable=True)
        self.channel.exchange_declare(exchange='customer_app_events', exchange_type="topic")

        self.channel.queue_declare(queue=self.queue)
        self.channel.queue_purge(queue=self.queue)
        self.channel.queue_bind(exchange="parking_events_exchange", queue=self.queue, routing_key=self.weight)

        # self.channel.queue_bind(exchange='parking_events_exchange', queue=self.queue)

        self.channel.basic_consume(on_message_callback=self.handle_parking_event,
                                   queue=self.queue,
                                   auto_ack=True)

        # result = self.channel.queue_declare(queue='parking_events_exchange', exclusive=True)
        # queue_name = result.method.queue

        self.billing_event_producer = BillingEventProducer(self.connection, self.worker_id)
        self.billing_event_producer.initialize_rabbitmq()

        self.customer_app_event_producer = CustomerEventProducer(self.connection, self.worker_id)
        self.customer_app_event_producer.initialize_rabbitmq()

        xprint("ParkingWorker {}: initialize_rabbitmq() called".format(self.worker_id))

    def handle_parking_event(self, ch, method, properties, body):
        # To implement - This is the callback that is passed to "on_message_callback" when a message is received

        xprint("ParkingWorker {}: handle_event() called".format(self.worker_id))
        # Handle the application logic and the publishing of events here
        json2python = json.loads(body)
        parkEvent = ParkingEvent(event_type=json2python['event_type'], car_number=json2python['car_number'],
                                 timestamp=json2python['timestamp'])
        # parkEvent = ParkingEvent(event_type=json2python['event_type'], car_number="abc",
        #                          timestamp=json2python['timestamp'])

        bad_message = json.dumps(vars(parkEvent))
        car_numbers = customers_database.values()
        if parkEvent.car_number in car_numbers:
            self.parking_events.append(parkEvent)
        else:
            self.channel.queue_declare(queue='parking_events_dead_letter_queue',
                                       arguments={
                                           "x-dead-letter-exchange": "",
                                           "x-dead-letter-routing-key": "parking_events_dead_letter_queue"
                                       })

            self.channel.basic_publish(exchange='',
                                       routing_key="parking_events_dead_letter_queue",
                                       body=bad_message)


        # xprint("test")
        # xprint(json2python)
        # self.parking_events.append(parkEvent)
        # message = json.dumps(vars(parkEvent))
        # self.channel.basic_publish(exchange='', body=parkEvent)

        customer_id = self.get_customer_id_from_parking_event(parkEvent)

        # self.channel.basic_publish(exchange='customer_app_events',
        #                            routing_key=customer_id,
        #                            body=message)
        self.customer_app_event_producer.publish_parking_event(customer_id, parkEvent)
        if customer_id is None:
            pass
        if parkEvent.event_type == "entry":
            # self.parking_state[customer_id] = parkEvent
            self.parking_state[parkEvent.car_number] = parkEvent.timestamp
            xprint(self.parking_state)
            # self.channel.basic_publish(exchange='customer_app_events', body=parkEvent)
        elif parkEvent.event_type == "exit":
            # entryEvent = self.parking_state[customer_id]
            xprint(self.parking_state)
            entryEvent = self.parking_state[parkEvent.car_number]
            self.parking_state.pop(parkEvent.car_number)
            if entryEvent is None:
                xprint("exit and no found entry :" + str(customer_id))
                return
            parking_time = self.calculate_parking_duration_in_seconds(entry_time=self.get_time(entryEvent),
                                                                      exit_time=self.get_time(parkEvent.timestamp))

            parking_cost = ((parking_time + 3599) / 3600) * cost_per_hour
            parking_cost = math.ceil(parking_cost) - 2
            billingEvent = BillingEvent(customer_id=customer_id, car_number=parkEvent.car_number,
                                        entry_time=entryEvent, exit_time=parkEvent.timestamp,
                                        parking_cost=parking_cost)

            self.channel.queue_declare(queue="billing_events")
            # self.channel.queue_bind(queue="billing_events", exchange="")

            # message2 = json.dumps(vars(billingEvent))
            self.customer_app_event_producer.publish_billing_event(billingEvent)
            self.billing_event_producer.publish(billingEvent)

    def get_time(self, timesp):
        result = timesp.split('.')[0]
        utc_dt = datetime.datetime.strptime(result, '%Y-%m-%dT%H:%M:%S')
        return utc_dt

    # Utility function to get the customer_id from a parking event
    def get_customer_id_from_parking_event(self, parking_event):
        customer_id = [customer_id for customer_id, car_number in customers_database.items()
                       if parking_event.car_number == car_number]
        if len(customer_id) is 0:
            xprint("{}: Customer Id for car number {} Not found".format(self.worker_id, parking_event.car_number))
            return None
        return customer_id[0]

    # Utility function to get the time difference in seconds
    def calculate_parking_duration_in_seconds(self, entry_time, exit_time):
        timedelta = (exit_time - entry_time).total_seconds()
        return timedelta

    def start_consuming(self):
        # To implement - Start consuming from Rabbit
        # self.channel.basic_consume(on_message_callback=self.handle_parking_event,
        #                            queue=self.queue,
        #                            auto_ack=True)
        self.channel.start_consuming()
        xprint("ParkingWorker {}: start_consuming() called".format(self.worker_id))

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
        # Reusing connection created in ParkingWorker
        self.channel = connection.channel()

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        # self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

        # self.channel = self.connection.channel()
        # self.channel.exchange_declare(exchange='')
        # self.channel.queue_declare(queue='billing_events')
        self.channel.queue_declare(queue="billing_events")
        xprint("BillingEventProducer {}: initialize_rabbitmq() called".format(self.worker_id))

    def publish(self, billing_event):
        xprint("BillingEventProducer {}: Publishing billing event {}".format(
            self.worker_id,
            vars(billing_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(billing_event)) to convert the parking_event object to JSON
        message = json.dumps(vars(billing_event))
        # self.channel.basic_publish(exchange=)
        self.channel.basic_publish(exchange='',
                                   routing_key="billing_events",
                                   body=message)

    def close(self):
        # Do not edit this method
        self.channel.close()


class CustomerEventProducer:

    def __init__(self, connection, worker_id):
        # Do not edit the init method.
        self.worker_id = worker_id
        # Reusing connection created in ParkingWorker
        self.channel = connection.channel()

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        # self.channel.queue_declare(queue=)
        self.channel.exchange_declare(exchange='customer_app_events', exchange_type="topic")

        xprint("CustomerEventProducer {}: initialize_rabbitmq() called".format(self.worker_id))

    def publish_billing_event(self, billing_event):
        xprint("{}: CustomerEventProducer: Publishing billing event {}".format(self.worker_id, vars(billing_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(billing_event)) to convert the parking_event object to JSON
        message = json.dumps(vars(billing_event))
        self.channel.basic_publish(exchange='customer_app_events',
                                   routing_key=billing_event.customer_id,
                                   body=message)


    def publish_parking_event(self, customer_id, parking_event):
        xprint("{}: CustomerEventProducer: Publishing parking event {} {}".
               format(self.worker_id, customer_id, vars(parking_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(parking_event)) to convert the parking_event object to JSON
        message = json.dumps(vars(parking_event))
        self.channel.basic_publish(exchange='customer_app_events',
                                   routing_key=customer_id,
                                   body=message)

    def close(self):
        # Do not edit this method
        self.channel.close()
