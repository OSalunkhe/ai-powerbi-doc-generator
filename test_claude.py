from dotenv import load_dotenv
from anthropic import Anthropic

# Reads the ANTHROPIC_API_KEY from your .env file
load_dotenv()

client = Anthropic()  # automatically picks up the key from the environment

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "In one sentence, what does a Power BI measure do?"}
    ]
)

print(response.content[0].text)