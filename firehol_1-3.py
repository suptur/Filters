import requests
import requests
import os
from tqdm import tqdm

# List of URLs to download
urls = [
"https://iplists.firehol.org/files/firehol_level1.netset",
"https://iplists.firehol.org/files/firehol_level2.netset",
"https://iplists.firehol.org/files/firehol_level3.netset",
####################---END----#############################
    # Add more URLs as needed
]

# Function to download a file and show progress
def download_file(url, dest_folder):
    filename = url.split("/")[-1]
    filepath = os.path.join(dest_folder, filename)
    with open(filepath, "wb") as file, requests.get(url, stream=True) as response:
        total_size = int(response.headers.get("content-length", 0))
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True, desc=f"Downloading {filename}")
        for data in response.iter_content(chunk_size=1024):
            file.write(data)
            progress_bar.update(len(data))
        progress_bar.close()

    return filepath

# Download files and merge into a single file
merged_lines = set()  # Using a set for faster duplicate removal
download_folder = "downloads"
os.makedirs(download_folder, exist_ok=True)
for url in urls:
    filepath = download_file(url, download_folder)
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
             if not line.startswith(("!", "#")):  # Exclude lines starting with "!"
                merged_lines.add(line.strip())

# Save updated file with unique lines and remove lines starting with "!"
merged_unique_file = "firehol_1-3.txt"
with open(merged_unique_file, "w", encoding="utf-8") as file:
    for line in sorted(merged_lines):  # Sort lines alphabetically
        file.write(line + "\n")

# Delete downloaded files and merged_unique.txt
download_folder = "downloads"
# os.remove(merged_unique_file)
for filename in os.listdir(download_folder):
    file_path = os.path.join(download_folder, filename)
    os.remove(file_path)
