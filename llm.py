from openai import OpenAI
from dotenv import load_dotenv
import os
from utils import read_config

load_dotenv()
BASE_URL = os.getenv("LLM_BASE_URL")

# Initialize the OpenAI API with your API key
client = OpenAI(
    api_key="koboldcpp",
    base_url=BASE_URL
)

def pre_process():
    # Read the config each time pre_process is called
    config = read_config()
    system_prompt = config['llm']['system_prompt']
    char = config['llm']['char']

    system_prompt = system_prompt.replace("{char}", char)
    return system_prompt

# Function to handle messages and stream response from OpenAI
def generate_llm(prompt):
    system_prompt = pre_process()
    response = client.chat.completions.create(
        model="koboldcpp/HF_SPACE_Tiefighter-13B",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    msg = response.choices[0].message.content
    return msg
