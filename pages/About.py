import streamlit as st

st.title("Open Files: A Streamlit Chatbot for Image Metadata Analysis")

st.header("Overview")
st.write("""
This project that analyzes image metadata and provides a comprehensive description of the image content. The chatbot uses the Gemini Pro AI vision API to extract metadata from images and generate a detailed response. Two modes image analysis and image: Metadata extraction and AI Vision.
""")

st.header("Features")
st.write("""
* Upload an image or provide a URL to analyze image metadata
* Get a comprehensive description of the image content, including scene understanding, object detection, image classification, image analysis, entity recognition, and contextual information
* Interact with the chatbot using natural language input
* View the chat history and previous responses
""")

st.header("Requirements")
st.write("""
* OpenRouter API key (environment variable `OPENROUTER_API_KEY`)
* Streamlit installed (`pip install streamlit`)
* Exiftool installed (`sudo apt install libimage-exiftool-perl`)

""")

st.header("Usage")
st.write("""
1. Run the chatbot by executing `streamlit run streamlit.py`
2. Upload an image or provide a URL to analyze image metadata
3. Interact with the chatbot using natural language input
4. View the chat history and previous responses
""")

st.header("Components")
st.write("""
* `streamlit.py`: The main Streamlit app that handles user input and displays chat responses
* `vision_func.py`: A Python module that provides the AI vision functionality using OpenRouter's API
""")

st.header("License")
st.write("""
This project is licensed under the MIT License. See `LICENSE` for details.
""")

st.header("Contributing")
st.write("""
Contributions are welcome! If you'd like to help improve the chatbot or add new features, please submit a pull request.
""")

## 👏 Acknowledgments
st.write("Special thanks to:")
st.write("🙏 **Google Gemini Pro API**: for providing the image analysis functionality")
st.write("🙏 **OpenRouter**: for routing the API")
st.write("🙏 **Streamlit**: for providing the chatbot framework")
st.write("🙏 **PyExifTool**: for providing a Python interface to Exiftool")
st.write("🙏 **Exiftool**: for providing a comprehensive metadata extraction tool")
## Additional
st.header("Additional Metadata Extraction")
st.write("The chatbot also extracts metadata from images using the [IPTC](https://iptc.org/standards/photo-metadata/) standards for image metadata.")
st.write("Examples of the metadata that can be extracted or written:")
st.write("*   **IPTC.Caption**: Extracting the image caption or description")
st.write("*   **IPTC.Keywords**: Extracting keywords or tags associated with the image")
st.write("*   **IPTC.Credit**: Extracting the credit or attribution information for the image creator")
st.write("*   **IPTC.Contact**: Extracting the contact information for the image creator or owner")

st.write("By incorporating IPTC metadata, the chatbot provides a more comprehensive understanding of the image content, including its context, meaning, and usage.")
