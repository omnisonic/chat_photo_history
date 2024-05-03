# 🎉 Open Files: A Streamlit Chatbot for Image Metadata Analysis 📸

## 📝 Overview
🌟 This project analyzes image metadata and provides a comprehensive description of the image content. The chatbot uses the Gemini Pro AI vision API to extract metadata from images and generate a detailed response. Two modes are available: image analysis and image metadata extraction. 🤖

## 🎯 Features
🔹 **Image Analysis**: Upload an image or provide a URL to analyze image metadata
💡 **Comprehensive Description**: Get a detailed description of the image content, including scene understanding, object detection, image classification, image analysis, entity recognition, and contextual information
💬 **Chatbot Interface**: Interact with the chatbot using natural language input
📝 **Chat History**: View the chat history and previous responses
- **Scene Understanding**: Identifying the context and setting of the image, such as indoor, outdoor, or specific locations.

- **Image Classification**: Categorizing the image into predefined categories, such as landscape, portrait, or abstract.
- **Image Analysis**: Analyzing the image's visual features, such as colors, textures, and shapes.
- **Entity Recognition**: Identifying and extracting specific information from the image, such as names, dates, or locations.
- **Contextual Information**: Providing additional information about the image, such as the photographer's intent or the image's historical significance.

By combining these features, our AI powered app aims provides a comprehensive and accurate description of the image content, making it easier to understand and analyze the image metadata.


## 🔑 Requirements
🔑 **OpenRouter API Key**: Set environment variable `OPENROUTER_API_KEY`
💻 **Streamlit**: Install using `pip install streamlit`
📈 **Exiftool**: Install using `sudo apt install libimage-exiftool-perl`

## 💻 Usage
1️⃣ Run the chatbot by executing `streamlit run streamlit.py`
2️⃣ Upload an image or provide a URL to analyze image metadata
3️⃣ Interact with the chatbot using natural language input
4️⃣ View the chat history and previous responses

## 🗃️ Components
📂 **streamlit.py**: The main Streamlit app that handles user input and displays chat responses
🔍 **vision_func.py**: A Python module that provides the AI vision functionality using OpenRouter's API

## 📝 License
🔓 This project is licensed under the MIT License. See `LICENSE` for details.

## 🤝 Contributing
🎉 Contributions are welcome! If you'd like to help improve the chatbot or add new features, please submit a pull request.

## 👏 Acknowledgments
🙏 **Google Gemini Pro API**: Special thanks to the Google Gemini Pro API for providing the image analysis functionality
🙏 **OpenRouter**: [OpenRouter](https://www.openrouter.com/) for routing the API
🙏 **Streamlit**: [Streamlit](https://streamlit.io/) for providing the chatbot framework
🙏 **PyExifTool**: [PyExifTool](https://pypi.org/project/PyExifTool/) for providing a Python interface to Exiftool
🙏 **Exiftool**: [Exiftool](https://exiftool.org/) for providing a comprehensive metadata extraction tool

## Additional
The chatbot also extracts metadata from images using the [IPTC](https://iptc.org/standards/photo-metadata/) standards for image metadata. Examples of the metadata that can be extracted or written:

*   **IPTC.Caption**: Extracting the image caption or description
*   **IPTC.Keywords**: Extracting keywords or tags associated with the image
*   **IPTC.Credit**: Extracting the credit or attribution information for the image creator
*   **IPTC.Contact**: Extracting the contact information for the image creator or owner

By incorporating IPTC metadata, the chatbot provides a more comprehensive understanding of the image content, including its context, meaning, and usage.

