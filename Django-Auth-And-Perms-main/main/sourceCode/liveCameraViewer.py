import zmq
import cv2
import numpy as np
import time

camera = cv2.VideoCapture(0)
try:
    frame, img = camera.read()
except:
    exit()
img = np.asarray(img)
time.sleep(10)
frame, img = camera.read()

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print(f"Received request: {message}")

    #  Do some 'work'
    try:
        frame, img = camera.read()
    except:
        print("Could not take an image")
        img = [1,1,1]
    img = np.asarray(img)

    #  Send reply back to client
    socket.send(img)

camera.release()