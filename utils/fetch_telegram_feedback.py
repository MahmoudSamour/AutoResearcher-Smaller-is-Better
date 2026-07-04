import os
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

def fetch_feedback():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing in .env!")
        return

    # Track the last update ID to only get NEW messages
    offset_file = os.path.join(os.path.dirname(__file__), 'last_update_id.txt')
    offset = 0
    if os.path.exists(offset_file):
        with open(offset_file, 'r') as f:
            offset = int(f.read().strip())

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={offset}"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if not data.get("ok"):
                print("Failed to fetch updates:", data)
                return
                
            messages = data.get("result", [])
            if not messages:
                print("No new feedback from Telegram.")
                # Ensure USER_FEEDBACK.txt is cleared if there's no new feedback for this cycle
                feedback_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'USER_FEEDBACK.txt')
                if os.path.exists(feedback_file):
                    os.remove(feedback_file)
                return

            highest_update_id = offset
            feedback_texts = []
            
            for update in messages:
                update_id = update.get("update_id")
                if update_id >= highest_update_id:
                    highest_update_id = update_id + 1
                
                message = update.get("message", {})
                chat = message.get("chat", {})
                text = message.get("text", "")
                
                # Only accept messages from the authorized user
                if str(chat.get("id")) == str(TELEGRAM_CHAT_ID) and text:
                    feedback_texts.append(text)

            # Save the new offset so we don't read these again
            with open(offset_file, 'w') as f:
                f.write(str(highest_update_id))

            # Write feedback to file for the AutoResearch agent to consume
            if feedback_texts:
                feedback_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'USER_FEEDBACK.txt')
                with open(feedback_file, 'w') as f:
                    f.write("--- USER TELEGRAM FEEDBACK ---\n")
                    f.write("\n".join(feedback_texts))
                print(f"Captured {len(feedback_texts)} new feedback messages to USER_FEEDBACK.txt!")

    except Exception as e:
        print(f"Error fetching Telegram updates: {e}")

if __name__ == "__main__":
    fetch_feedback()
