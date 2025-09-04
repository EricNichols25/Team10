import cv2
import numpy as np
import os

USB_PATH = "/home/kali/Desktop/TestImages"  
OUTPUT_PATH = "./detected_deathstar_images"
os.makedirs(OUTPUT_PATH, exist_ok=True)

def find_red_circles(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Red HSV ranges
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    # Combine both red masks
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # Smooth to reduce noise
    red_mask_blur = cv2.GaussianBlur(red_mask, (9, 9), 2)

    # Detect circles
    circles = cv2.HoughCircles(red_mask_blur, 
                               cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=100, param2=30,
                               minRadius=20, maxRadius=200)

    if circles is not None:
        return np.uint16(np.around(circles[0]))
    else:
        return None

def crop_around_circle(image, x, y, r, padding=20):
    h, w = image.shape[:2]

    # Define square bounding box around the circle
    x1 = max(x - r - padding, 0)
    y1 = max(y - r - padding, 0)
    x2 = min(x + r + padding, w)
    y2 = min(y + r + padding, h)

    return image[y1:y2, x1:x2]

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

        circles = find_red_circles(image)

        if circles is not None:
            # You can optionally loop over all circles, but we'll just use the first one
            x, y, r = circles[0]
            cropped_img = crop_around_circle(image, x, y, r)

            # Save the cropped image
            output_path = os.path.join(OUTPUT_PATH, filename)
            cv2.imwrite(output_path, cropped_img)
            detected += 1
            print(f"[+] Detected and cropped red circle in: {filename}")
        else:
            print(f"[-] No red circle in: {filename}")

    print(f"\nTotal images with red circles cropped and saved: {detected}")

if __name__ == "__main__":
    process_images()
