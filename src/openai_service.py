import os
import openai
from dotenv import load_dotenv

class OpenAIClient:
    def __init__(self):
        """
        Initialize the OpenAI Client.
        Dynamically load the API key from .env for local testing or Docker secrets.
        """
        env_file_path = os.getenv('ENV_PATH', '.env')  # Default to .env for local testing
        if os.path.exists(env_file_path):
            load_dotenv(env_file_path)
        else:
            print(f"No .env file found at {env_file_path}. Assuming Docker secrets.")

        self.api_key = os.getenv('API_KEY')
        if not self.api_key:
            raise ValueError("API key not set. Ensure API_KEY is provided in the .env file or Docker secret.")

        openai.api_key = self.api_key

    def answer_email(self, email):
        """
        Send a prompt to the OpenAI API and get the response.
        :param prompt: The prompt text to send.
        :return: The response text from the model.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": 'Your persona is James Dawson. Answer the following scam email by outputting only the body text and not the subject. If possible answer in the language the email is in. Keep it short. Please go along with the scam and try to keep the conversation going. Do not give any personal information or banking details. The output will not be altered and has to be a finished piece of text: \n' + email}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    def answer_email_with_pdf(self, email):
        """
        Send a prompt to the OpenAI API and get the response.
        :param email: The prompt text to send.
        :return: The response text from the model.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": 'Your persona is James Dawson. Answer the following email by outputting only the body text and not the subject. If possible answer in the language the email is in. Keep it short. The output will not be altered and has to be a finished piece of text. The answer will include a pdf file containing information relevant to the email being answered: \n' + email}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def fill_pdf(self, email):
        """
        Send a prompt to the OpenAI API and get the response.
        :param email: The email text to send.
        :return: The response text from the model.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": 'Based on the following email, please output text that is relevant in order to fill a pdf file to be sent, and output only the text. Please leave no spaces to be filled. The output will not be altered and has to be a finished piece of text: \n' + email}],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    def generate_pdf_name(self, email):
        """
        Send a prompt to the OpenAI API and get the response.
        :param prompt: The prompt text to send.
        :return: The response text from the model.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": 'Based on the following email come up with a name for a PDF file, without the .pdf extension, please only output the name: \n' + email}],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None