import cv2
from time import sleep
camera = cv2.VideoCapture(0)
sleep(3)

status, img = camera.read()
print(status)
print(img)

sleep(3)

camera.release()

sleep(3)

camera.release()
