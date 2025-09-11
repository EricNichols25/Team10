import os
import hashlib
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Directory/Output settings
INPUT_DIR = ''
OUTPUT_DIR = ''

# Same hardcoded AES-256 key
SECRET_KEY = b'\xe3\xb2\xf9\x8d\x17\xc6j\x99\xfd\xb6\xa6M\xef\xd7\xfd\x14\x91~\x14c\xd5&\xa7\xc2\xc1\x85\xb7X\xa1\x0c:\xd7'

def decrypt_file(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()

    iv = content[:16]
    ciphertext = content[16:]

    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    filename = os.path.basename(filepath).replace('.enc', '')
    dec_path = os.path.join(OUTPUT_DIR, filename)
    with open(dec_path, 'wb') as f:
        f.write(plaintext)

    # MD5 verification
    md5_path = filepath.replace('.enc', '.md5')
    if os.path.exists(md5_path):
        with open(md5_path, 'r') as f:
            expected_md5 = f.read().strip()
        actual_md5 = hashlib.md5(plaintext).hexdigest()
        if expected_md5 == actual_md5:
            print(f"[OK] {filename}: MD5 verified")
        else:
            print(f"[!] {filename}: MD5 mismatch!")

def decrypt_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for file in os.listdir(INPUT_DIR):
        if file.endswith('.enc'):
            decrypt_file(os.path.join(INPUT_DIR, file))

if __name__ == '__main__':
    decrypt_all()
    print(f"[+] Decryption complete. Output in '{OUTPUT_DIR}'")

