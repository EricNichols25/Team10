import cv2 as cv
import numpy as np
import sys

img = cv.imread("C:/Users/19375/Documents/Team Projects II/images/image9.png")

if img is None:
    sys.exit("Could not read the image.")

cv.imshow("Display Window", img)
k = cv.waitKey(0)

# find any red area in the image
red_color = np.array([255, 0, 0])
