import os
import openai

class OpenAIClient:
    def __init__(self, api_key=None):
        """
        Initialize the OpenAI Client.
        :param api_key: OpenAI API key. If None, will look for OPENAI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("API key not provided and OPENAI_API_KEY environment variable not set.")
        openai.api_key = self.api_key

    def answer_email(self, prompt):
        """
        Send a prompt to the OpenAI API and get the response.
        :param prompt: The prompt text to send.
        :return: The response text from the model.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": 'Answer the following email by outputting only the body text and not the subject: \n' + prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def fill_pdf(self, prompt):
        """
        Send a prompt to the OpenAI API and get the response.
        :param prompt: The prompt text to send.
        :return: The response text from the model.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": 'Based on the following email, please output some text that is somewhat relevant in order to fill a pdf file to be sent: \n' + prompt}],
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    def generate_pdf_name(self, prompt):
        """
        Send a prompt to the OpenAI API and get the response.
        :param prompt: The prompt text to send.
        :return: The response text from the model.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": 'Based on the following email come up with a name for a PDF file, without the .pdf extension, please only output the name: \n' + prompt}],
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None