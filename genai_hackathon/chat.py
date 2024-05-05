import logging
import json
import vertexai
from IPython.display import Markdown
import textwrap
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig, ChatSession, Content, Part

# Configuration setup
PROJECT_ID = "ewx-ddaas-staging"
REGION = "europe-west1"

PROJECT_ID="qwiklabs-gcp-04-51f95fb097d0"
REGION="us-central1"

def initialize_vertexai():
    vertexai.init(project=PROJECT_ID, location=REGION)
    logging.info("Vertex AI initialized.")


def to_markdown(text: str) -> Markdown:
    """Convert text to markdown format, handling list items."""
    return Markdown(textwrap.indent(text.replace('•', '  *'), '> '))

class ChatBot:
    """ChatBot class for handling conversation with a generative model."""
    def __init__(self, user_id, model_name="gemini-1.5-pro-preview-0409"):
        initialize_vertexai()
        self.user_id = user_id
        self.model: GenerativeModel = GenerativeModel(
            model_name,
        system_instruction=[
            "Don't use technical terms in your response",
            "Always try to relate with the kids hobby and medical record",
        ],
        )
        self.conversation: ChatSession = None
        self.chat_history: [] = self.load_chat_history()
        logging.info("ChatBot initialized.")

    def load_chat_history(self) -> [Content]:
        """Load chat history from a JSON file, specific to the user_id."""
        try:
            with open(f"{self.user_id}_history.json", "r") as file:
                # TODO: fix load chat history
                return Content.from_dict(json.load(file))
        except FileNotFoundError:
            return [
                # Content(role="user", parts=[Part.from_text("I like Elsa from Frozen")])
            ]  # Return an empty list if no history file exists

    def save_chat_history(self):
        """Save chat history to a JSON file, specific to the user_id."""
        with open(f"{self.user_id}_history.json", "w") as file:
            json.dump(self.chat_history, file)

    def start_chat(self):
        """Start a chat session, ensuring conversation history is applied."""
        if not self.conversation:
            self.conversation = self.model.start_chat(
                history=self.chat_history
            )
        logging.info("Chat session started.")

    def send_chat_message(self, user_input: str, temperature: float = 0.7) -> str:
        """Send a user prompt to the model and return the response in JSON format."""
        if not self.conversation:
            self.start_chat()
        try:
            # TODO: enhance GenerationConfig
            # TODO: add system instruction
            #
            prompt = Content(role="user", parts=[Part.from_text(user_input)])
            response = self.conversation.send_message(prompt,
                                                      generation_config=GenerationConfig(temperature=temperature),
                                                      stream=True)
            model_response = ''.join(chunk.text for chunk in response)
            # This is needed to save the chat history for the next conversation session.
            self.chat_history.append({"role": "user", "parts": {"text": user_input}})
            self.chat_history.append({"role": "model", "parts": {"text": model_response}})
            self.save_chat_history()
            # logging.info("Chat response received.")
            return json.dumps({"text": model_response})
        except Exception as e:
            logging.error(f"Error sending chat message: {e}")
            return json.dumps({"error": str(e)})


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    user_id = input("What is your name:")
    chat_bot = ChatBot(user_id)
    chat_bot.start_chat()
    # Provide background of the kid:
    kid_info = "I love Elsa from movie Frozen. I have a medical record of Leukemia."
    initial_prompt = f"Please greet the user with his or her name in a friendly manner by asking how are they feeling base on his or her hobby and medical record. Hobby: <{kid_info}>, Name: <{user_id}>."
    response = chat_bot.send_chat_message(initial_prompt)  # Send initial greeting
    print(response)
    while True:
        user_input = input("")
        if user_input.lower() == 'exit':
            chat_bot.save_chat_history()
            break
        response = chat_bot.send_chat_message(user_input)
        print(response)
