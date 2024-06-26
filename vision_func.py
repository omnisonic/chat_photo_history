import base64
import requests
import json
import os
from openai import OpenAI



def ai_vision(image_input, api_key):
    print(f"\n ai vision func called \n ")
    base64_image = None
    url = None

    if hasattr(image_input, 'read'):
        # Streamlit UploadedFile object
        print(f"Uploaded file: {image_input.name}")
        image_data = image_input.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        url = f"data:image/jpeg;base64,{base64_image}"
    elif 'https://' in str(image_input).lower():
        # If image_input is a URL, use it as is
        url = image_input
        print(f"Image URL: {url}")
    else:
        # If image_input is a file path, read the file and encode it as base64
        with open(image_input, "rb") as f:
            image_data = f.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        url = f"data:image/jpeg;base64,{base64_image}"


    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        data=json.dumps({
            "model": "google/gemini-pro-vision",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze the image and provide a comprehensive description, including: Scene understanding: What is happening in the scene? What are the main objects, people, and activities depicted? Object detection: Identify and list the individual objects present in the image, including their types, quantities, and locations. Image classification: What is the dominant theme or category of the image? What tags or labels would you assign to the image? Image analysis: Describe the image's characteristics, including colors, textures, shapes, and any notable features. Entity recognition: Identify specific entities, such as people, organizations, or locations, depicted in the image only mention them if you highg certainty. Contextual information: Provide any relevant contextual information about the image, such as the time of day, weather, or setting. Please provide a detailed and structured response, using headings and bullet points where necessary, to help me understand the image and its contents. Approximate date of the image."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url
                            }
                        }
                    ]
                }
            ]
        })
    )

    try:
        response = response.json()["choices"][0]["message"]["content"] 

        print(f" \n line ~52 from vision vunc: the api response {response[:100]}") # use [:100] to see only the first 200 characters
        return response
    except KeyError as e:
        print(f"Error: {e}")
        print("API response:")
        print(response.json())
        response = None

