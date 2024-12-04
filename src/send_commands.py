# send_command.py
import requests
import sys

# address = "http://localhost:8005"
address = "http://167.235.242.47:8005"

def start_conversation(email, subject):
    url = address + "/start_conversation"
    response = requests.post(url, json={"email": email, "subject": subject})
    print("Response:", response.json())

def get_status():
    url = address + "/status"
    response = requests.get(url)
    print("Response:", response.json())
    
def send_first_email(sender, subject, body):
    url = address + "/send_first_email"
    response = requests.post(url, json={"sender": sender, "subject": subject, "body": body})
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
    elif command == "send_first_email" and len(sys.argv) == 5:
        sender = sys.argv[2]
        subject = sys.argv[3]
        body = sys.argv[4]
        send_first_email(sender, subject, body)
    else:
        print("Invalid command or arguments.")
