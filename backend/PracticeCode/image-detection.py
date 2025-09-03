import cv2

print(cv2.__version__)

image = cv2.imread('images/image9.png', cv2.IMREAD_UNCHANGED)

if image is None:
    print("Error: Could not load the image.")
else:
    cv2.imshow('PNG Image Display', image)

    cv2.waitKey(0)

    cv2.destroyAllWindows()
