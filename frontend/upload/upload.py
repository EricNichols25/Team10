
from importlib_metadata import files
import requests
import glob


url = "http://localhost:3001/upload"
files = glob.glob("CroppedImages/*.png")
for file in files:
    with open(file, "rb") as f:
        response = requests.post(url, files={"file": f}, timeout=10)
        print(response.text)