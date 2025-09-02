import cv2
import numpy as np
import os

USB_PATH = ""  
OUTPUT_PATH = "./detected_deathstar_images"
os.makedirs(OUTPUT_PATH, exist_ok=True)

def is_red_circle_present(image):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Red ranges
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # reducing noise
    red_mask_blur = cv2.GaussianBlur(red_mask, (9, 9), 2)

    # Circle Detection
    circles = cv2.HoughCircles(red_mask_blur, 
                               cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=100, param2=30,
                               minRadius=20, maxRadius=200)

    # Return True if circles are found
    return circles is not None

def process_images():
    detected = 0
    for filename in os.listdir(USB_PATH):
        if not filename.lower().endswith('.png'):
            continue

        img_path = os.path.join(USB_PATH, filename)
        image = cv2.imread(img_path)

        if image is None or image.shape[:2] != (1024, 1024):
            print(f"Skipping invalid image: {filename}")
            continue

        if is_red_circle_present(image):
            cv2.imwrite(os.path.join(OUTPUT_PATH, filename), image)
            detected += 1
            print(f"[+] Detected red circle in: {filename}")
        else:
            print(f"[-] No red circle in: {filename}")

    print(f"\nTotal images with red circles detected: {detected}")

if __name__ == "__main__":
    process_images()
