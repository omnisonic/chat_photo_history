import streamlit as st
from exiftool import ExifToolHelper
from os import getenv
from openai import OpenAI

# Streamlit page configuration
st.set_page_config(page_title="ExifTool Metadata Viewer", layout="wide")

def display_metadata(file_path):
    # Use ExifTool to extract metadata
    with ExifToolHelper() as et:
        metadata = et.get_metadata(file_path)
        return metadata

# UI for file uploader
st.title("ExifTool Metadata Viewer")
uploaded_file = st.file_uploader("Choose an image file", type=['jpg', 'jpeg', 'png', 'gif', 'tiff'])

if uploaded_file is not None:
    # Save the uploaded file to a temporary file to pass to ExifTool
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Fetch and display the metadata
    metadata = display_metadata(uploaded_file.name)
    if metadata:
        # Convert metadata to a string
        metadata_str = "\n".join(f"{k}: {v}" for data in metadata for k, v in data.items())

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenRouter AI")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not getenv("OPENROUTER_API_KEY"):
        st.info("Please add your OpenRouter API key to environment variable OPENROUTER_API_KEY to continue.")
        st.stop()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=getenv("OPENROUTER_API_KEY"),
    )
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(
        model="mistralai/mixtral-8x7b-instruct",
        messages=[{"role": "system", "content": "You are answering questions about photo metadata."}, {"role": "context", "content": metadata_str}] + st.session_state.messages + [{"role": "user", "content": prompt}],
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
