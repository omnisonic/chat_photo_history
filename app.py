from flask import Flask, request, jsonify, render_template
import base64
import os
import requests
import json

app = Flask(__name__)

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_image():
    print(request.files)  # Print the request files dictionary
    print(request.form)  # Print the request form data
    if 'file' not in request.files:
        print("No file part")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    print(file.filename)  # Print the file name
    # ... rest of your code ...


    image_data = file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")

    #... rest of your code remains the same...


    print("Sending API request to OpenRouter...")

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        },
        data=json.dumps({
            "model": "google/gemini-pro-vision",  # Optional
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

    print("API request sent!")

    if response.status_code == 200:
        print(f"API response received successfully! \n response: \n {response.json}")
        return jsonify(response.json())
    else:
        print("API response failed:", response.status_code)
        return jsonify({"error": "API response failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
