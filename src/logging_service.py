import json
import hashlib
import os
from datetime import datetime

def get_conversation_id(sender):
    """
    Generate a unique conversation ID based on the sender's email.
    :param sender: The sender's email.
    :return: The conversation ID.
    """
    # Generate a unique conversation ID based on the sender's email
        # Create a SHA-256 hash of the email
    email_hash = hashlib.sha256(sender.encode()).hexdigest()
    # Return a shortened version if you prefer
    return email_hash[:12]  # Shorten to the first 10 characters if needed

def create_new_conversation_log(sender):
    """
    Create a new conversation log file.
    :param sender: The sender of the conversation.
    :return: The ID of the conversation.
    """
    # Create a new conversation log json file with an unique id based on the sender's email
    conversation_id = get_conversation_id(sender)
    conversation_log = {
        "conversation_id": conversation_id,
        "sender": sender,
        "messages": []
    }
    if not os.path.exists("../logs"):
        os.makedirs("../logs")

    with open(f"../logs/{conversation_id}.json", "w") as file:
        json.dump(conversation_log, file)
    return conversation_id
    

def add_to_log(conversation_id, sender, message, timestamp):
    """
    Add a message to the conversation log.
    :param conversation_id: The ID of the conversation.
    :param sender: The sender of the message.
    :param message: The message content.
    :param timestamp: The timestamp of the message.
    """
    # Add the message to the conversation log

    with open(f"../logs/{conversation_id}.json", "r") as file:
        conversation_log = json.load(file)

        conversation_log["messages"].append({"from": sender, "message": message, "timestamp": timestamp})

    with open(f"../logs/{conversation_id}.json", "w") as file:
        json.dump(conversation_log, file)


    
def get_conversation_log(conversation_id):
    """
    Get the conversation log for a given conversation ID.
    :param conversation_id: The ID of the conversation.
    :return: The conversation log.
    """
    # Get the conversation log for the given conversation ID
    with open(f"/..conversation_logs/{conversation_id}.json", "r") as file:
        conversation_log = json.load(file)
    return conversation_log

def get_conversation_length(conversation_id):
    """
    Get the length of a conversation (number of messages).
    :param conversation_id: The ID of the conversation.
    :return: The length of the conversation.
    """
    # Get the length of the conversation
    with open(f"../logs/{conversation_id}.json", "r") as file:
        conversation_log = json.load(file)
        return len(conversation_log["messages"])

def get_system_info():
    """
    Get information on the system such as how many total and active conversations.
    :return: System information.
    """
    # Get system information
    pass

def get_latest_messages(conversation_id, num_messages):
    """
    Get the latest messages from a conversation.
    :param conversation_id: The ID of the conversation.
    :param num_messages: The number of messages to retrieve.
    :return: The latest messages.
    """
    # Get the latest messages from the conversation
    pass

def add_honeytoken_id(honeytoken_id, conversation_id):
    """
    Add a honeytoken ID to a conversation.
    :param honeytoken_id: The honeytoken ID.
    :param conversation_id: The ID of the conversation.
    """
    # Add the honeytoken ID to the conversation
    if not os.path.exists("../logs/{conversation_id}.json"):
        return "Conversation does not exist."
    
    with open(f"../logs/{conversation_id}.json", "r") as file:
        conversation_log = json.load(file)
        conversation_log["honeytoken_id"] = honeytoken_id
        conversation_log["interactions"] = []

def get_honeytoken_id(conversation_id):
    """
    Get the honeytoken ID associated with a conversation.
    :param conversation_id: The ID of the conversation.
    :return: The honeytoken ID.
    """
    # Get the honeytoken ID associated with the conversation
    with open(f"../logs/{conversation_id}.json", "r") as file:
        conversation_log = json.load(file)
        honeytoken_id = conversation_log.get("honeytoken_id")

    return honeytoken_id

def add_honeytoken_interaction(honeytoken_id, ip_address, user_agent, timestamp):
    """
    Add an interaction to a honeytoken.
    :param honeytoken_id: The honeytoken ID.
    :param ip_address: The IP address of the interaction.
    :param user_agent: The user agent of the interaction.
    :param timestamp: The timestamp of the interaction.
    """
    for file in os.listdir("../logs"):
        with open(f"../logs/{file}", "r") as f:
            conversation_log = json.load(f)
            if conversation_log.get("honeytoken_id") == honeytoken_id:
                conversation_log["interactions"].append({"ip_address": ip_address, "user_agent": user_agent, "timestamp": timestamp})
                with open(f"../logs/{file}", "w") as f:
                    json.dump(conversation_log, f)
                return "Interaction added to honeytoken log."
            
# Path for the queue file
QUEUE_FILE_PATH = 'response_queue.json'

def datetime_to_string(dt):
    """Convert a datetime object to a string for JSON serialization."""
    return dt.isoformat()

def string_to_datetime(dt_str):
    """Convert a string to a datetime object for JSON deserialization."""
    return datetime.fromisoformat(dt_str)

def save_queue_to_file(queue):
    """Save the response queue to a JSON file."""
    with open(QUEUE_FILE_PATH, 'w') as file:
        json.dump(
            [{"email_id": entry["email_id"], "response_time": datetime_to_string(entry["response_time"])} for entry in queue],
            file,
            indent=4
        )

def load_queue_from_file():
    """Load the response queue from a JSON file."""
    if os.path.exists(QUEUE_FILE_PATH):
        with open(QUEUE_FILE_PATH, 'r') as file:
            loaded_entries = json.load(file)
            return [{"email_id": entry["email_id"], "response_time": string_to_datetime(entry["response_time"])} for entry in loaded_entries]
    return []    
