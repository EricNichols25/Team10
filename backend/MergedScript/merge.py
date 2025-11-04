import os
import cv2
import numpy as np
import hashlib
from secrets import token_bytes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from time import perf_counter

# === CONFIGURATION PATHS ===
USB_PATH = "./images"  # initial input images
OUTPUT_PATH = "./final_detected_images"
OUTPUT_DIR_ENC = "./encrypted_images"
OUTPUT_DIR_DEC = "./decrypted_images"

os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(OUTPUT_DIR_ENC, exist_ok=True)
os.makedirs(OUTPUT_DIR_DEC, exist_ok=True)

# === SECRET KEY FOR AES ===
# Must be exactly 32 bytes for AES-256
SECRET_KEY = b"0123456789ABCDEF0123456789ABCDEF"

# === STAGE 1: Detect & Crop Red Circles ===

def find_red_circles(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 98, 97])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 98, 97])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    red_mask_blur = cv2.GaussianBlur(red_mask, (9, 9), 2)

    # Detect circles
    circles = cv2.HoughCircles(
        red_mask_blur,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=50,
        param1=100,
        param2=30,
        minRadius=20,
        maxRadius=200,
    )

    if circles is not None:
        return np.uint16(np.around(circles[0]))
    else:
        return None

def crop_around_circle(image, x, y, r, padding=20):
    h, w = image.shape[:2]
    x1 = max(x - r - padding, 0)
    y1 = max(y - r - padding, 0)
    x2 = min(x + r + padding, w)
    y2 = min(y + r + padding, h)
    return image[y1:y2, x1:x2]

def process_images(input_folder, output_folder):
    detected = 0
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(".png"):
            continue

        img_path = os.path.join(input_folder, filename)
        image = cv2.imread(img_path)

        if image is None:
            print(f"Skipping invalid image: {filename}")
            continue

        circles = find_red_circles(image)
        if circles is not None:
            x, y, r = circles[0]
            cropped_img = crop_around_circle(image, x, y, r)
            output_path = os.path.join(output_folder, filename)

            if cropped_img.size > 0:
                cv2.imwrite(output_path, cropped_img)
                detected += 1
                print(f"[+] Detected and cropped red circle in: {filename}")
            else:
                print(f"[-] Cropping resulted in an empty image for: {filename}")
        else:
            print(f"[-] No red circle in: {filename}")

    print(f"\nTotal images with red circles cropped and saved: {detected}")

# === STAGE 2: Encrypt Cropped Images ===

def encrypt_file(filepath, output_folder=OUTPUT_DIR_ENC):
    with open(filepath, "rb") as f:
        plaintext = f.read()
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()

    iv = token_bytes(16)
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    enc_path = os.path.join(output_folder, os.path.basename(filepath) + ".enc")
    with open(enc_path, "wb") as f:
        f.write(iv + ciphertext)

def encrypt_all(input_folder=OUTPUT_PATH):
    for file in os.listdir(input_folder):
        if file.lower().endswith(".png"):
            encrypt_file(os.path.join(input_folder, file))
    print(f"[+] Encryption complete. Output in '{OUTPUT_DIR_ENC}'")

# === STAGE 3: Decrypt & Verify ===

def decrypt_file(filepath, output_folder=OUTPUT_DIR_DEC):
    with open(filepath, "rb") as f:
        content = f.read()
    iv, ciphertext = content[:16], content[16:]
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    filename = os.path.basename(filepath).replace(".enc", "")
    dec_path = os.path.join(output_folder, filename)
    with open(dec_path, "wb") as f:
        f.write(plaintext)

def decrypt_all(input_folder=OUTPUT_DIR_ENC):
    for file in os.listdir(input_folder):
        if file.endswith(".enc"):
            decrypt_file(os.path.join(input_folder, file))
    print(f"[+] Decryption complete. Output in '{OUTPUT_DIR_DEC}'")

# === MAIN PIPELINE ===

if __name__ == "__main__":
    start = perf_counter()

    PASSES = 2
    temp_input = USB_PATH
    for i in range(PASSES):
        temp_output = f"./pass_{i+1}_output"
        os.makedirs(temp_output, exist_ok=True)
        print(f"--- PASS {i+1} ---")
        process_images(temp_input, temp_output)
        temp_input = temp_output

    # Final output folder
    if os.path.exists(OUTPUT_PATH):
        for f in os.listdir(OUTPUT_PATH):
            os.remove(os.path.join(OUTPUT_PATH, f))
        os.rmdir(OUTPUT_PATH)
    os.rename(temp_output, OUTPUT_PATH)

    print(f"\nTotal time for {PASSES} passes: {perf_counter() - start:.2f} seconds")

    # Step 2: Encrypt
    print("\n=== Step 2: Encrypt ===")
    encrypt_all()

    # Step 3: Decrypt
    print("\n=== Step 3: Decrypt ===")
    decrypt_all()

    print("\n[✓] All stages complete.")
