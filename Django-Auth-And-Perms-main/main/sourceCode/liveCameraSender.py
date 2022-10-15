import zmq
import matplotlib.pyplot as plt

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5557")

for request in range(10):
    print("Sending request")
    socket.send_string("hi")

    #  Get the reply.
    message = socket.recv()
    print(message)
    plt.show(message[0])