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
        "text": "Analyze the image and provide a comprehensive description, including: Scene understanding: What is happening in the scene? What are the main objects, people, and activities depicted? Object detection: Identify and list the individual objects present in the image, including their types, quantities, and locations. Image classification: What is the dominant theme or category of the image? What tags or labels would you assign to the image? Image analysis: Describe the image's characteristics, including colors, textures, shapes, and any notable features. Entity recognition: Identify specific entities, such as people, organizations, or locations, depicted in the image. Contextual information: Provide any relevant contextual information about the image, such as the time of day, weather, or setting. Please provide a detailed and structured response, using headings and bullet points where necessary, to help me understand the image and its contents. Approximate date of the image"
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
# get the content from the response
print(response.json()["choices"][0]["message"]["content"])
