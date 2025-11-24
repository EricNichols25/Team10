import os
import cv2
import numpy as np
import sys
import zipfile
import shutil
import glob
from secrets import token_bytes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from time import perf_counter, sleep


#Config Paths
USB_PATH = "./images"  #initial input images
OUTPUT_PATH = "./final_detected_images"
OUTPUT_DIR_ENC = "./encrypted_images"
OUTPUT_DIR_DEC = "./decrypted_images"
ZIP_PATH = "./detected_images.zip"  # Zip file path

# === SECRET KEY FOR AES ===
SECRET_KEY = b"0123456789ABCDEF0123456789ABCDEF"


def find_red_circles(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Refined range
    lower_red1 = np.array([0, 150, 150])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 150, 150])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    #Noise Reduction
    kernel = np.ones((3,3), np.uint8)
    red_mask = cv2.erode(red_mask, kernel, iterations=1)
    red_mask = cv2.dilate(red_mask, kernel, iterations=2)

    red_mask_blur = cv2.GaussianBlur(red_mask, (9, 9), 2)

    circles = cv2.HoughCircles(
        red_mask_blur,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=50,
        param1=100,
        param2=40,
        minRadius=15,
        maxRadius=100,
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

# Zip the detected image

def zip_images(input_folder, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(input_folder):
            if file.lower().endswith('.png'):
                zipf.write(os.path.join(input_folder, file), file)
    print(f"[+] Zipping complete. Zip file created at '{zip_path}'")

# === Encrypt the files

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

def encrypt_zip(zip_path):
    encrypt_file(zip_path)
    print(f"[+] Encryption complete. Encrypted zip in '{OUTPUT_DIR_ENC}'")

# Decrypt and unzip

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

def unzip_images(zip_path, output_folder):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(output_folder)
    print(f"[+] Unzipping complete. Images extracted to '{output_folder}'")

def decrypt_and_unzip():
    enc_zip_path = os.path.join(os.path.basename(ZIP_PATH) + ".enc")
    if os.path.exists(enc_zip_path):
        decrypt_file(enc_zip_path)
        dec_zip_path = os.path.join(OUTPUT_DIR_DEC, os.path.basename(ZIP_PATH))
        unzip_images(dec_zip_path, OUTPUT_DIR_DEC)
        print(f"[+] Decryption and unzipping complete. Output in '{OUTPUT_DIR_DEC}'")
    else:
        print("[-] Encrypted zip file not found.")




#Main Pipeline
if __name__ == "__main__":

    start = perf_counter()

    # pi or server
    environment = sys.argv[1] if len(sys.argv) > 1 else "server"
    
    if environment.lower() == "server":
        from server import transmission
        print("Running in SERVER mode.")

        os.makedirs(OUTPUT_DIR_DEC, exist_ok=True)

        
        print("\n=== Step 4: Transmission ===")
        transmission()
        
        sleep(2)

        # Step 5: Decrypt & Unzip
        print("\n=== Step 5: Decrypt & Unzip ===")
        decrypt_and_unzip()
        print(f"\nDecryption and unzipping took {perf_counter() - start:.2f} seconds")
        print("\n[✓] All stages complete.")

        exit(0)
    
    # === This section will only be ran inside the Pi === #
    
    from pi import transmission
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    os.makedirs(USB_PATH, exist_ok=True)
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    os.makedirs(OUTPUT_DIR_ENC, exist_ok=True)


    class NewDirHandler(FileSystemEventHandler):
        def __init__(self, observer_instance, path_to_watch):
            super().__init__()
            self.observer_instance = observer_instance
            self.path_to_watch = path_to_watch
        
        def on_created(self, event):
            if event.is_directory :
                
                print(f"[+] New directory created: {event.src_path}")
                
                if event.src_path == self.path_to_watch:
                    print('[+] Stopping observer as target directory is created.')
                    self.observer_instance.stop()

    observer = Observer()
    event_handler = NewDirHandler(observer, "/media/usb1")
    observer.schedule(event_handler, path="/media", recursive=False)
    
    observer.start()

    print("[*] Monitoring '/media' for new directories...")

    try:
        while observer.is_alive():
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()
        
    print("\n[✓] Detected target directory. Moving images down...")

    for img in glob.glob("/media/usb1/*.png"):
        shutil.move(img, os.path.join(USB_PATH, os.path.basename(img)))


    ### === 
    print("\n[*] Starting image processing pipeline...")

    if not os.path.exists(USB_PATH):
        print(f"Error: Input directory '{USB_PATH}' does not exist. Please create it and add your PNG images there.")
        exit(1)

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

    print(f"\n[✓] Total time for {PASSES} passes: {perf_counter() - start:.2f} seconds")
    start = perf_counter()

    # Step 2: Zip
    print("\n=== Step 2: Zip ===")
    zip_images(OUTPUT_PATH, ZIP_PATH)
    print(f"\n[✓] Zipping took {perf_counter() - start:.2f} seconds")
    start = perf_counter()

    # Step 3: Encrypt
    print("\n=== Step 3: Encrypt ===")
    encrypt_zip(ZIP_PATH)
    print(f"\n[✓] Encryption took {perf_counter() - start:.2f} seconds")
    start = perf_counter()

    print('Letting pi rest for a bit...')
    sleep(3)

    # Step 4: Transmission
    print("\n=== Step 4: Transmission ===")
    transmission(f"{OUTPUT_DIR_ENC}/{os.path.basename(ZIP_PATH)}.enc")
    print(f"\nTransmission took {perf_counter() - start:.2f} seconds")
    start = perf_counter()

    if environment.lower() == "pi":
        print(f"\n[✓] Transmission complete. Exiting on Pi side.")
        exit(0)

