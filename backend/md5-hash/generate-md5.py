import hashlib
import os
import glob # glob finds all matching file types (ex: *.png)
import json

folder = "../detected_deathstar_images"  # change to folder where vulnerabilities images are saved
hashes = {}

for filepath in glob.glob(os.path.join(folder, "*.png")):
    with open(filepath, "rb") as f:
        file_bytes = f.read()
        hash_md5 = hashlib.md5(file_bytes).hexdigest()
        hashes[os.path.basename(filepath)] = hash_md5

# Save hashes to file
with open("image_hashes.json", "w") as f:
    json.dump(hashes, f, indent=4)

print("Hashes saved to image_hashes.json")
