import grpc
from proto import restaurant_pb2
from proto import restaurant_pb2_grpc

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = restaurant_pb2_grpc.RestaurantStub(channel)
        responseFoodOrder = stub.FoodOrder(restaurant_pb2.RestaurantRequest(orderID="12345abc",
                                                                    items=["fizzy drink", "water", "water"]))
        responseDrinkOrder = stub.DrinkOrder(restaurant_pb2.RestaurantRequest(orderID="2436234abc",
                                                                    items=["fizzy drink", "water", "water"]))
        responseDessertOrder = stub.DessertOrder(restaurant_pb2.RestaurantRequest(orderID="12565asdfbc",
                                                                    items=["ice cream", "chocolate cake", "water"]))
    print("FoodOrder received: ", responseFoodOrder)
    print("DrinkOrder received: ", responseDrinkOrder)
    print("DessertOrder received: ", responseDessertOrder)


if __name__ == '__main__':
    run()
