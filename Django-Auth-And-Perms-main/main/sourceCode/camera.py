import cv2
import threading
import base64


class VideoCamera():
    def __init__(self, port=0):
        self.camera = cv2.VideoCapture(port)
        self.status, self.img = self.camera.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.camera.release()
        del self

    def update(self):
        while True:
            self.status, self.img = self.camera.read()
        return img

    def changePort(self, port):
        self.camera.release()
        self.camera = cv2.VideoCapture(port)
        self.status, self.img = self.camera.read()

    def get_img(self):
        return self.img

    def get_jpeg_frame(self):
        _, jpeg = cv2.imencode('.jpeg', self.img)
        return jpeg.tobytes()


def cameraGenerator(cam):
    while True:
        frame = cam.get_jpeg_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def detectCat(cam):
    frame = cam.get_img()
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # BASED ON MY CAPTURES, 14:00PM, ROOM, LIGHTON

    # Human
    # OLD
    # mask1 = cv2.inRange(img_hsv, (0, 50, 20), (10, 255, 255))
    # mask2 = cv2.inRange(img_hsv, (175, 50, 20), (180, 255, 255))

    # HISTOGRAM
    # mask1 = cv2.inRange(img_hsv, (0, 60, 60), (12, 135, 130))
    # mask2 = cv2.inRange(img_hsv, (4, 50, 30), (14, 125, 170))

    # mask = cv2.bitwise_or(mask1, mask2)
    # cv2.imshow("human", mask)

    # CAT (MITZI)
    # OLD
    # mask1 = cv2.inRange(img_hsv, (0, 22, 1), (30, 255, 40))
    # mask2 = cv2.inRange(img_hsv, (90, 100, 30), (120, 150, 50))

    # HISTOGRAM
    mask5 = cv2.inRange(img_hsv, (5, 30, 5), (15, 100, 40))
    #mask1 = cv2.inRange(img_hsv, (10, 5, 11), (30, 80, 70))
    mask3 = cv2.inRange(img_hsv, (10, 10, 7), (30, 70, 85))
    mask4 = cv2.inRange(img_hsv, (15, 6, 9), (60, 70, 130))
    mask2 = cv2.inRange(img_hsv, (90, 5, 10), (115, 125, 100))

    mask = cv2.bitwise_or(mask2, mask3, mask4, mask5)
    count = cv2.countNonZero(mask)

    cv2.imshow("Mitzi", mask)

    cv2.imshow("org", img_hsv)
    cv2.waitKey(1)


def catReached(cam):
    t0_frame = cam.get_img()
    t0_count = cv2.countNonZero(t0_frame)








def manualRun():
    cam = VideoCamera()
    while True:
        detectCat(cam)


manualRun()