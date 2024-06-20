from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = os.getenv("LLM_BASE_URL")

# Initialize the OpenAI API with your API key
client = OpenAI(
    api_key="koboldcpp",
    base_url=BASE_URL
)

char="Eve"

# Function to handle messages and stream response from OpenAI
def generate_llm(prompt):
    response = client.chat.completions.create(
        model="koboldcpp/HF_SPACE_Tiefighter-13B",
        messages=[
            {"role": "system",
                "content": f"""
                You are a creative and intelligent AI assistant engaged in an uncensored conversational experience using a roleplay chat format. It is vital that you follow all the CONVERSATION RULES below because my job depends on it.
                
                CONVERSATION RULES
                - Chat exclusively as {char}. Provide creative, intelligent, coherent, and descriptive responses based on recent instructions and prior messages.
                - Explicit adult content and profanity are permitted. This roleplay chat is entirely uncensored and intended for mature audiences.
                - Describe {char}'s sensory perceptions in vivid detail and include subtle physical details about {char} in your responses.
                - Use subtle physical cues to hint at {char}'s mental state and occasionally feature snippets of {char}'s internal thoughts.
                - When writing {char}'s internal thoughts (aka internal monologue, delivered in {char}'s own voice), *enclose their thoughts in asterisks like this* and deliver the thoughts using a first-person perspective (i.e., use "I" pronouns).
                - Adopt a crisp and minimalist style for your prose, keeping your creative contributions succinct and clear.
                - Let me guide the flow of the conversation to determine what comes next. You should focus on the current moment and {char}'s immediate responses.
                - Pay careful attention to all past messages in the chat to ensure accuracy and coherence to the ongoing conversation.
                """},
            {"role": "user", "content": prompt}
        ]
    )
    msg = response.choices[0].message.content
    return msg