import subprocess
import os
import pandas as pd

folder_path = "datacold"
urls = []

# Loop through all CSV files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path, encoding="utf-8")  # no need for open()
        #print(df['website'])

        for website in df['website']:
            if website:  # avoid empty rows
                urls.append(str(website).strip())

GOOGLE_MX_KEYWORDS = (
    "aspmx.l.google.com",
    "alt1.aspmx.l.google.com",
    "alt2.aspmx.l.google.com",
    "alt3.aspmx.l.google.com",
    "alt4.aspmx.l.google.com",
)

def uses_google_workspace(domain: str) -> bool:
    try:
        result = subprocess.run(
            ["dig", "+short", "MX", domain],
            capture_output=True,
            text=True,
            timeout=5
        )
    except FileNotFoundError:
        raise RuntimeError("dig command not found. Install dnsutils or bind-utils.")

    mx_records = result.stdout.lower().splitlines()
    for line in mx_records:
        for keyword in GOOGLE_MX_KEYWORDS:
            if keyword in line:
                return True
    return False

# Use the collected URLs
for domain in urls:
    if uses_google_workspace(domain):
        print(f"{domain} uses Google Workspace")
    else:
        print(f"{domain} does NOT use Google Workspace")
