import os
import sys
import glob
import urllib.request
import urllib.parse
import json

# Manually load credentials from root .env
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, val = line.strip().split('=', 1)
                if key == "TELEGRAM_BOT_TOKEN":
                    TELEGRAM_BOT_TOKEN = val.strip("'\"")
                elif key == "TELEGRAM_CHAT_ID":
                    TELEGRAM_CHAT_ID = val.strip("'\"")

def send_to_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing in .env!")
        return

    # Telegram message limit is 4096 chars
    message = message[:4090]
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("Telegram report sent successfully!")
    except Exception as e:
        print(f"Failed to send Telegram report: {e}")

if __name__ == "__main__":
    # Find the most recent report in the reports directory
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
    if not os.path.exists(reports_dir):
        print("No reports directory found.")
        sys.exit(0)
        
    list_of_files = glob.glob(os.path.join(reports_dir, '*.md'))
    
    if not list_of_files:
        print("No reports found to send.")
        sys.exit(0)

    latest_file = max(list_of_files, key=os.path.getctime)
    
    with open(latest_file, 'r') as f:
        content = f.read()

    send_to_telegram(content)
