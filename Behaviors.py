import cv2
import numpy as np
import VisionUtils
import Utils
from time import time


class FollowLine:
    def __init__(self, parent):
        self.rover = parent


    def isUpdate(self):
        pass

    def update(self):
        self.__findLines()


    def __findLineDirections(self):
        # Inputs

        # Possible Pairs (8,6) (9,12) (12,16)
        gridW = 9
        gridH = 12


        # Processing
        img = self.rover.camera.read()

        rImg = VisionUtils.isolateColor(img, [150, 75, 75], [30, 255, 255])
        rGray = cv2.cvtColor(rImg, cv2.COLOR_BGR2GRAY)
        ret, rThresh = cv2.threshold(rGray, 50, 255, cv2.THRESH_BINARY)

        # Resize
        small = cv2.resize(rThresh,    (9, 12), interpolation=cv2.INTER_AREA)

        # Debug
        big   = cv2.resize(  small, (640, 480), interpolation=cv2.INTER_AREA)  #Delete- for debug only
        cv2.imshow('frame', big)
        cv2.waitKey(5000)



    def __findLines(self):
        img   = self.rover.camera.read()
        print('doing')
        rImg  = VisionUtils.isolateColor(img,   [150, 75, 75],  [30, 255, 255])
        rGray = cv2.cvtColor(rImg, cv2.COLOR_BGR2GRAY)
        ret, rThresh = cv2.threshold(rGray, 50, 255, cv2.THRESH_BINARY)

        # Make the image small to reduce line-finding processing times
        small = cv2.resize(rThresh, (64, 48), interpolation=cv2.INTER_AREA)

        cv2.imshow('Thresh', rThresh)

        start = time()
        # lines = cv2.HoughLinesP(edges, 1, np.pi, threshold=25, minLineLength=50, maxLineGap=10)
        lines = cv2.HoughLinesP(small, 1, np.pi/200, threshold=25, minLineLength=20, maxLineGap=10)
        print(time() - start)

        if lines is not None:
            lines = [line[0] for line in lines]
            self.__combineLines(lines)

        cv2.waitKey(1000)
        return lines

    def __combineLines(self, lines):
        """ Combines similar lines into one large 'average' line """
        maxAngle = 30

        def getAngle(line):
            # Turn angle from -180:180 to just 0:180
            angle = Utils.lineAngle(line[:2], line[2:])

            if angle < 0: angle += 180
            return angle

        def lineFits(checkLine, combo):
            """ Check if the line fits within this group of combos by checking it's angle """
            checkAngle = getAngle(checkLine)
            for line in combo:
                angle = getAngle(line)
                difference = abs(checkAngle - angle)
                if difference < maxAngle or 180 - difference < maxAngle:
                    return True
            return False


        # [[l1, l2, l3], [l4, l5, l6]
        lineCombos    = []
        unsortedLines = lines

        # Get Line Combos
        while len(unsortedLines) > 0:
            checkLine = unsortedLines.pop(0)

            sorted = False
            for i, combo in enumerate(lineCombos):
                if lineFits(checkLine, combo):
                    lineCombos[i].append(checkLine.tolist())
                    sorted = True
                    break

            if not sorted:
                lineCombos.append([checkLine.tolist()])
        print("Len:", len(lineCombos), "\nSorted:\n",lineCombos)


        # Average Combo Groups
        combinedCombos = []  # [L1, L2, L3]
        for combo in lineCombos:
            avgLine = [0, 0, 0, 0]  # Average start and end points
            sampleSize = len(combo)

            for line in combo:
                avgLine = [avgLine[i] + line[i] for i in range(0, 3)]
            avgLine = [c / sampleSize for c in avgLine]
            combinedCombos.append(avgLine)

        # Draw Line Combos and Final Lines
        img = self.rover.camera.read()
        for i, combo in enumerate(lineCombos):
            for x1, y1, x2, y2 in combo:
                x1 *= 10
                y1 *= 10
                x2 *= 10
                y2 *= 10

                cv2.line(img, (x1, y1), (x2, y2), (80*i, 80*i, 80*i), 2)
        for x1, y1, x2, y2 in combinedCombos:
            x1 *= 10
            y1 *= 10
            x2 *= 10
            y2 *= 10

            cv2.line(img, (x1, y1), (x2, y2), (80, 80, 80), 8)

        cv2.imshow('final', img)
        cv2.waitKey(5000)

        # # DELETE LATER, DEBUG ONLY
        # img = self.rover.camera.read()
        # for x1, y1, x2, y2 in lines:
        #     x1 *= 10
        #     y1 *= 10
        #     x2 *= 10
        #     y2 *= 10
        #     # x1, y1, x2, y2 = line[0]
        #     cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        #
        # cv2.imshow('final', img)
        # cv2.waitKey(5000)