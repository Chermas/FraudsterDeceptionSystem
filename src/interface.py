from flask import Flask, render_template, request
import requests
import os
import dotenv

app = Flask(__name__)

dotenv.load_dotenv()

address = os.getenv('MAIN_URL')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "send":
            email = request.form.get("email")
            subject = request.form.get("subject")
            body = request.form.get("message")

            # Send POST request to your API for sending a new email
            try:
                url = address + "/send_first_email"
                response = requests.post(url, json={"sender": email, "subject": subject, "body": body})
                response.raise_for_status()
                return f"New email sent successfully! Response: {response.json()}"
            except requests.exceptions.RequestException as e:
                return f"Error sending new email: {e}", 500

        elif action == "reply":
            email = request.form.get("reply_email")
            subject = request.form.get("reply_subject")

            # Send POST request to your API for replying to an email
            try:
                url = address + "/start_conversation"
                response = requests.post(url, json={"email": email, "subject": subject})
                response.raise_for_status()
                return f"Reply sent successfully! Response: {response.json()}"
            except requests.exceptions.RequestException as e:
                return f"Error sending reply: {e}", 500

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8006)
