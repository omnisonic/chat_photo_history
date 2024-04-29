import requests
import json
import os
import base64

# Load the image file
with open("image.jpg", "rb") as f:
    image_data = f.read()

# Base64 encode the image data
base64_image = base64.b64encode(image_data).decode("utf-8")

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",

  },
  data=json.dumps({
    "model": "google/gemini-pro-vision", # Optional
"messages": [
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "What's in this image?"
      },
      {
        "type": "image_url",
        "image_url": {
          "url": f"data:image/jpeg;base64,{base64_image}" 
        }
      }
    ]
  }
]
  })
)

print(response.json())