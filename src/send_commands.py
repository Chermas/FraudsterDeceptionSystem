# send_command.py
import requests
import sys

def start_conversation(email, subject):
    url = "http://localhost:5000/start_conversation"
    response = requests.post(url, json={"email": email, "subject": subject})
    print("Response:", response.json())

def get_status():
    url = "http://localhost:5000/status"
    response = requests.get(url)
    print("Response:", response.json())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: send_command.py <command> [arguments]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start_conversation" and len(sys.argv) == 4:
        email = sys.argv[2]
        subject = sys.argv[3]
        start_conversation(email, subject)
    elif command == "status":
        get_status()
    else:
        print("Invalid command or arguments.")
