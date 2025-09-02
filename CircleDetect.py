import cv2 as cv
import numpy as np
import sys

img = cv.imread("C:/Users/19375/Documents/Team Projects II/images/image9.png")

if img is None:
    sys.exit("Could not read the image.")

#cv.imshow("Display Window", img)
#k = cv.waitKey(0)

def identifyRedCircles(image):
    # convert to HSV image
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    lowerRed1 = np.array([0, 70, 50])
    upperRed1 = np.array([10, 255, 255])
    lowerRed2 = np.array([170, 70, 50])
    upperRed2 = np.array([180, 255, 255])

    #create color mask to identify red areas in images (works)
    mask1 = cv.inRange(hsv, lowerRed1, upperRed1)
    mask2 = cv.inRange(hsv, lowerRed2, upperRed2)
    redMask = mask1 | mask2

    # check to see if red areas in the mask are circles and not false positives
    circles = cv.HoughCircles(redMask, cv.HOUGH_GRADIENT, dp=1, minDist=50, param1=100, param2=30,
                            minRadius=20, maxRadius=200)


    #cv.imshow("Display Window", img)
    cv.imshow("Mask", redMask)
    k = cv.waitKey(0)

    return circles is not None

identifyRedCircles(img)

#get the HSV color code
#red = np.uint8([[[255, 0, 0]]])
#hsvRed = cv.cvtColor(red, cv.COLOR_BGR2HSV)
#print(hsvRed)


# find any red area in the image
#red_color = np.array([255, 0, 0])