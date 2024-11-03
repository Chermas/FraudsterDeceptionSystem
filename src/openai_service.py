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

    def send_prompt(self, prompt):
        """
        Send a prompt to the OpenAI API and get the response.
        :param prompt: The prompt text to send.
        :return: The response text from the model.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": 'Answer the following email: \n' + prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def send_prompts(self, prompts, model='gpt-3.5-turbo', temperature=0.7, max_tokens=150):
        """
        Send multiple prompts to the OpenAI API and get the responses.
        :param prompts: A list of prompt texts to send.
        :return: A list of response texts.
        """
        responses = []
        for prompt in prompts:
            response = self.send_prompt(prompt, temperature)
            responses.append(response)
        return responses
