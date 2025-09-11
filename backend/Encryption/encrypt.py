import os
import hashlib
from secrets import token_bytes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Directory/output settings
INPUT_DIR = '/home/kali/Desktop/detected_deathstar_images'
OUTPUT_DIR = '/home/kali/Desktop/encrypted_output'

 Hardcoded 32-byte AES-256 key
SECRET_KEY = b'\xe3\xb2\xf9\x8d\x17\xc6j\x99\xfd\xb6\xa6M\xef\xd7\xfd\x14\x91~\x14c\xd5&\xa7\xc2\xc1\x85\xb7X\xa1\x0c:\xd7'

def encrypt_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    padder = padding.PKCS7(128).padder()
    padded = padder.update(data) + padder.finalize()

    iv = token_bytes(16)

    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    encrypted_data = iv + ciphertext
    filename = os.path.basename(filepath)
    enc_path = os.path.join(OUTPUT_DIR, filename + '.enc')
    with open(enc_path, 'wb') as f:
        f.write(encrypted_data)

    md5 = hashlib.md5(data).hexdigest()
    with open(os.path.join(OUTPUT_DIR, filename + '.md5'), 'w') as f:
        f.write(md5)

def encrypt_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for file in os.listdir(INPUT_DIR):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            encrypt_file(os.path.join(INPUT_DIR, file))

if __name__ == '__main__':
    encrypt_all()
    print(f"[+] All files encrypted using AES. Output in '{OUTPUT_DIR}'")
