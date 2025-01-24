from flask import Flask, request, redirect
import logging_service as logs
import datetime as datetime

app = Flask(__name__)

@app.route("/<token>")
def track_and_redirect(token):
    # Get the client IP from X-Forwarded-For or fallback to remote_addr
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    referrer = request.referrer

    timestamp = datetime.datetime.now().isoformat()
    # Log the unique token and visitor information
    logs.add_token_interaction(token, visitor_ip, user_agent, timestamp)
    print(f"Received a request from {visitor_ip} with user agent {user_agent} and referrer {referrer} for token {token}")

    # Redirect to the target URL
    return redirect("https://google.com", code=302)  # Replace with the actual target URL


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)