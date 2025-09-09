import hashlib
import json
import os

folder = "../detected_deathstar_images"  # change to folder where vulnerabilities images are saved

# Load hashes from file
with open("image_hashes.json", "r") as f:
    generated_hashes = json.load(f)

# Verify each hash
for filename, expected_hash in generated_hashes.items():
    filepath = os.path.join(folder, filename)
    if not os.path.exists(filepath):
        print(f"{filename}: MISSING")
        continue

    with open(filepath, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    if file_hash == expected_hash:
        print(f"{filename}: OK")
    else:
        print(f"{filename}: FAILED (expected {expected_hash}, got {file_hash})")
