
from openai import OpenAI
from os import getenv

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
  base_url="https://openrouter.ai/api/v1/chat/completions",
  api_key=getenv("OPENROUTER_API_KEY"),
)

completion = client.chat.completions.create(

  model="google/gemini-pro-vision",
  messages=[
    {
      "role": "user",
      "content": "what is in this image",
    },
    { "type": "image_url",
     "image_url": {
         "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
     }
     }
  ],
)
print(completion.choice[0])