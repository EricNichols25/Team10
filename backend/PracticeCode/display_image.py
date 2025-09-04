import cv2
import numpy as np

# Read the PNG image
image = cv2.imread("images/image9.png")

# Check if the image was loaded successfully
if image is None:
    print("Error: Could not load image.")
else:
    # Convert to HSV (better for color filtering)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define red color ranges (red wraps around the hue spectrum)
    lower_red1 = (0, 100, 100)
    upper_red1 = (10, 255, 255)
    lower_red2 = (160, 100, 100)
    upper_red2 = (180, 255, 255)

    # Create masks and combine them
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Blur to reduce noise
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)

    # Detect circles using Hough Transform
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                               param1=50, param2=30, minRadius=5, maxRadius=50)
    
    # Draw detected circles
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for (x, y, r) in circles[0, :]:
            # Define bounding box coordinates
            x1, y1 = max(x - r, 0), max(y - r, 0)
            x2, y2 = min(x + r, image.shape[1]), min(y + r, image.shape[0])

            # Crop the region of interest (ROI)
            cropped = image[y1:y2, x1:x2]

            # Show cropped image
            cv2.imshow("Cropped Circle", cropped)
            cv2.waitKey(0)
            
    cv2.destroyAllWindows()
