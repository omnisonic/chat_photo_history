import streamlit as st
from exiftool import ExifToolHelper
from os import getenv
from openai import OpenAI
import pathlib

# Streamlit page configuration
st.set_page_config(page_title="AI CHAT with Metadata PHOTOS", layout="wide", initial_sidebar_state="expanded")

css = '''
<style>
    [data-testid="stSidebar"]{
        min-width: 400px;
        max-width: 800px;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

# Display a sample photo in the sidebar
st.sidebar.image("sample_photo.jpg", width=200)



# UI for file uploader
st.title("AI CHAT with IPTC Metadata PHOTOS")


uploaded_file = st.file_uploader("Choose an image file", type=['jpg', 'jpeg', 'png', 'gif', 'tiff'])

def display_metadata(file_path):
    # Use ExifTool to extract metadata
    with ExifToolHelper() as et:
        metadata = et.get_metadata(file_path)
        return metadata
    

# metadata_str = "No metadata found Please upload a valid image file with IPTC or Exif metadata. Ask the User to drag use photo to the Drag and drop section do upload photo, or use the Browse files button" # Default value to prompt user to upload a file with metadata.  


# Add a button to load the sample photo
if st.sidebar.button("Load Sample Photo"):
    st.session_state.sample_photo = "sample_photo.jpg"
    st.session_state.messages = []
    # Upload the sample image file
    st.image("sample_photo.jpg", caption="sample Image", use_column_width=True)

if "sample_photo" in st.session_state:
    st.image(st.session_state.sample_photo, caption="sample Image", use_column_width=True)

# else:
#     metadata_str = "No metadata found Please upload a valid image file with metadata. Ask the User to drag use photo to the Drag and drop section do upload photo, or use the Browse files button" # Default value to prompt user to upload a file with metadata.  



if uploaded_file is not None:
    # Reset the chat history
    st.session_state.messages = []
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
else:
    sample_photo = "sample_photo.jpg"
    metadata = display_metadata(sample_photo)
    metadata_str = "\n".join(f"{k}: {v}" for data in metadata for k, v in data.items())




st.sidebar.title("💬 Chatbot")
st.sidebar.caption("🚀 A streamlit chatbot powered by OpenRouter")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Upload a photo with meta data and I will answer your questions"}]

for msg in st.session_state.messages:
    st.sidebar.chat_message(msg["role"]).write(msg["content"])

prompt = st.sidebar.chat_input("Ask a question ...")

if prompt:
    if not getenv("OPENROUTER_API_KEY"):
        st.info("Please add your OpenRouter API key to environment variable OPENROUTER_API_KEY to continue.")
        st.stop()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=getenv("OPENROUTER_API_KEY"),
    )
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.sidebar.chat_message("user").write(prompt)
    response = client.chat.completions.create(
        model="mistralai/mixtral-8x7b-instruct",
        messages=[{"role": "system", "content": f"You are answering questions about photo metadata. You specialize photo meta data.  You should alert the user if there is no meta DATA. The metadata is: {metadata_str}."}] + st.session_state.messages + [{"role": "user", "content": prompt}],
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.sidebar.chat_message("assistant").write(msg)
