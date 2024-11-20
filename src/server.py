from flask import Flask, request, redirect
import logging_service as logs

app = Flask(__name__)

@app.route("/<token>")
def track_and_redirect(token):
    # `token` is a dynamic part of the URL and will capture any token value
    visitor_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    referrer = request.referrer

    timestamp = request.headers.get('Date')
    # Log the unique token and visitor information
    logs.add_honeytoken_interaction(token, visitor_ip, user_agent, timestamp)

    # Redirect to the target URL
    return redirect("https://google.com", code=302)  # Replace with the actual target URL


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)