import grpc
import sys
from proto import restaurant_pb2
from proto import restaurant_pb2_grpc
from concurrent import futures

RESTAURANT_ITEMS_FOOD = ["chips", "fish", "burger", "pizza", "pasta", "salad"]
RESTAURANT_ITEMS_DRINK = ["water", "fizzy drink", "juice", "smoothie", "coffee", "beer"]
RESTAURANT_ITEMS_DESSERT = ["ice cream", "chocolate cake", "cheese cake", "brownie", "pancakes", "waffles"]

class Restaurant(restaurant_pb2_grpc.RestaurantServicer):

    def FoodOrder(self, request, context):
        items = request.items
        status = 0
        for item in items:
            if item not in RESTAURANT_ITEMS_FOOD:
                # return restaurant_pb2.RestaurantResponse(orderID=request.orderID, status=1)
                status = 1
                break
        return restaurant_pb2.RestaurantResponse(orderID=request.orderID, status=status)
    
    def DrinkOrder(self, request, context):
        items = request.items
        status = 0
        for item in items:
            if item not in RESTAURANT_ITEMS_DRINK:
                status = 1
                break
        return restaurant_pb2.RestaurantResponse(orderID=request.orderID, status=status)
    
    def DessertOrder(self, request, context):
        items = request.items
        status = 0
        for item in items:
            if item not in RESTAURANT_ITEMS_DESSERT:
                status = 1
                break
        return restaurant_pb2.RestaurantResponse(orderID=request.orderID, status=status)


def serve():

    # Logic goes here
    # Remember to start the server on localhost and a port defined by the first command line argument
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    restaurant_pb2_grpc.add_RestaurantServicer_to_server(Restaurant(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
