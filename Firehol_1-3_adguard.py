import requests
import os
import logging
from tqdm import tqdm
import threading

# Configure logging
logging.basicConfig(filename='script.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# ===== SETTINGS =====
# List of URLs to download
urls = [
"https://iplists.firehol.org/files/firehol_level1.netset",
"https://iplists.firehol.org/files/firehol_level2.netset",
"https://iplists.firehol.org/files/firehol_level3.netset",
    # Add more URLs here
]

# Where to store temporary downloaded files
download_folder = "downloads_ipsets"

# Path inside GitHub repo to store final firehol.txt
output_folder_in_repo = os.path.join("Filters")  # This will be lists/firehol.txt
output_file_path = os.path.join(output_folder_in_repo, "firehol_1-3_ADGUARD.txt")

# ===== FUNCTIONS =====
def download_file(url, dest_folder):
    """Download a single file with a progress bar."""
    try:
        filename = url.split("/")[-1]
        filepath = os.path.join(dest_folder, filename)
        with open(filepath, "wb") as file, requests.get(url, stream=True) as response:
            total_size = int(response.headers.get("content-length", 0))
            progress_bar = tqdm(total=total_size, unit="B", unit_scale=True, desc=f"Downloading {filename}")
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                progress_bar.update(len(data))
            progress_bar.close()
    except Exception as e:
        logging.error(f"Failed to download file from {url}: {str(e)}")

def convert_line(line):
    """Convert IPv4 address to uBlock-style ||address^ format."""
    return "||" + line.strip() + "^"

def download_files(urls, dest_folder, max_concurrent=100):
    """Download multiple files concurrently."""
    threads = []
    for url in urls:
        thread = threading.Thread(target=download_file, args=(url, dest_folder))
        threads.append(thread)
        thread.start()

        if len(threads) >= max_concurrent:
            for thread in threads:
                thread.join()
            threads = []

    for thread in threads:
        thread.join()

# ===== MAIN SCRIPT =====
if __name__ == "__main__":
    os.makedirs(download_folder, exist_ok=True)          # Temp folder for downloads
    os.makedirs(output_folder_in_repo, exist_ok=True)    # Ensure output folder exists

    # Download files
    download_files(urls, download_folder)

    # Process and merge files
    merged_lines = set()
    for filename in os.listdir(download_folder):
        filepath = os.path.join(download_folder, filename)
        with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                if not line.startswith(("@@", "!", "#")) and line.strip():
                    merged_lines.add(convert_line(line))

    # Save merged file to the GitHub repo folder
    with open(output_file_path, "w", encoding="utf-8") as file:
        for line in sorted(merged_lines):
            file.write(line + "\n")

    # Cleanup downloaded temp files
    for filename in os.listdir(download_folder):
        os.remove(os.path.join(download_folder, filename))
