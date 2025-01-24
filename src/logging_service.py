import json
import hashlib
import os
from datetime import datetime
import uuid

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

    if os.path.exists(f"../logs/{conversation_id}.json"):
        print(f"Conversation log already exists for {conversation_id}")
        return conversation_id

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

def add_honeytoken_id(honeytoken_id, conversation_id):
    """
    Add a honeytoken ID to a conversation.
    :param honeytoken_id: The honeytoken ID.
    :param conversation_id: The ID of the conversation.
    """
    # Add the honeytoken ID to the conversation
    if not os.path.exists(f"../logs/{conversation_id}.json"):
        print(f"Conversation does not exist. for file {conversation_id}")
        return "Conversation does not exist."
    print(f"Adding honeytoken ID to conversation. {honeytoken_id} to {conversation_id}")
    with open(f"../logs/{conversation_id}.json", "r") as file:
        conversation_log = json.load(file)
        conversation_log["honeytoken_id"] = honeytoken_id
        conversation_log["interaction"] = []
        with open(f"../logs/{conversation_id}.json", "w") as f:
            json.dump(conversation_log, f)
    return "Honeytoken ID added to conversation."

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

def has_honeytoken_id(conversation_id):
    """
    Check if a conversation has a honeytoken ID.
    :param conversation_id: The ID of the conversation.
    :return: True if the conversation has a honeytoken ID, False otherwise.
    """
    # Check if the conversation has a honeytoken ID
    with open(f"../logs/{conversation_id}.json", "r") as file:
        conversation_log = json.load(file)
        return "honeytoken_id" in conversation_log

def add_token_interaction(token_id, ip_address, user_agent, timestamp):
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
            if conversation_log.get("honeytoken_id") == token_id:
                conversation_log["interaction"].append({"ip_address": ip_address, "user_agent": user_agent, "timestamp": timestamp})
                with open(f"../logs/{file}", "w") as f:
                    json.dump(conversation_log, f)
                return "Interaction added to honeytoken log."
            if conversation_log.get("signature_id") == token_id:
                conversation_log["interaction"].append({"ip_address": ip_address, "user_agent": user_agent, "timestamp": timestamp})
                with open(f"../logs/{file}", "w") as f:
                    json.dump(conversation_log, f)
                return "Interaction added to signature log."
            
def add_signature_id(conversation_id):
    """
    Add a honeytoken ID to a conversation.
    :param honeytoken_id: The honeytoken ID.
    :param conversation_id: The ID of the conversation.
    """
    # Add the honeytoken ID to the conversation
    if not os.path.exists(f"../logs/{conversation_id}.json"):
        print(f"Conversation does not exist. for file {conversation_id}")
        return "Conversation does not exist."
    signature_id = uuid.uuid4().hex
    print(f"Adding signature ID to conversation. {signature_id} to {conversation_id}")
    with open(f"../logs/{conversation_id}.json", "r") as file:
        conversation_log = json.load(file)
        conversation_log["signature_id"] = signature_id
        conversation_log["interactions"] = []
        with open(f"../logs/{conversation_id}.json", "w") as f:
            json.dump(conversation_log, f)
    return "Signature ID added to conversation."

def get_signature_id(conversation_id):
    """
    Get the honeytoken ID associated with a conversation.
    :param conversation_id: The ID of the conversation.
    :return: The honeytoken ID.
    """
    # Get the honeytoken ID associated with the conversation
    with open(f"../logs/{conversation_id}.json", "r") as file:
        conversation_log = json.load(file)
        signature_id = conversation_log.get("signature_id")

    return signature_id

def has_signature_id(conversation_id):
    """
    Check if a conversation has a signature ID.
    :param conversation_id: The ID of the conversation.
    :return: True if the conversation has a signature ID, False otherwise.
    """
    # Check if the conversation has a signature ID
    with open(f"../logs/{conversation_id}.json", "r") as file:
        conversation_log = json.load(file)
        return "signature_id" in conversation_log
            
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
