import cv2

# Read the PNG image
image = cv2.imread("images/image9.png")

# Check if the image was loaded successfully
if image is None:
    print("Error: Could not load image.")
else:
    # Display the image in a window
    cv2.imshow("Image", image)
    
    # Wait for a key press and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()