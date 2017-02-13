import cv2
import numpy as np
import VisionUtils


class FollowLine:
    def __init__(self, parent):
        self.rover = parent


    def isUpdate(self):
        pass

    def update(self):
        self.__findLines()

    def __findLines(self):
        print("Doing thing!")

        img   = self.rover.camera.read()

        # Isolate the red
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lowerRed = np.array([  0,  50, 110])
        upperRed = np.array([ 30, 255, 255])
        mask = cv2.inRange(hsv, lowerRed, upperRed)
        rImg = cv2.bitwise_and(img, img, mask=mask)





        ret, rThresh = cv2.threshold(rImg, 90, 255, cv2.THRESH_BINARY_INV)
        edges = cv2.Canny(rThresh, 20, 40)

        cv2.imshow('r', rThresh)
        cv2.imshow('e', rImg)

        lines = cv2.HoughLines(image=edges, rho=1, theta=np.pi/180, threshold=100) # 1, np.pi / 180, 200)
        if lines is None:
            # cv2.imshow('Frame', gray)
            cv2.waitKey(3000)
            return




        for line in lines[:10]:
            for rho, theta in line:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))

                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        print("Found lines: ", len(lines))

        cv2.imshow('Edge', img)
        cv2.waitKey(4500)

    def __prototypeFindLines(self):
        # Unadvanced color thresholding