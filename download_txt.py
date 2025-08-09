import requests

# List of URLs to download
urls = [
    "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/unbreak.txt",
    # Add more URLs as needed
]

# Download files
for url in urls:
    filename = url.split("/")[-1]  # Save as last part of URL
    print(f"Downloading {url} → {filename}")
    r = requests.get(url)
    r.raise_for_status()
    with open(filename, "wb") as f:
        f.write(r.content)

print("All files downloaded.")
