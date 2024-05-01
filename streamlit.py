import streamlit as st
from exiftool import ExifToolHelper
from os import getenv
from openai import OpenAI
import pathlib
import requests
from io import BytesIO
from urllib.parse import urlparse

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

# Download file
file_obj = None

@st.cache_data
def download_file(url):
    headers = {'User-Agent': 'My Streamlit App (https://chat-photo-history.streamlit.app/)'}
    
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        return BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        st.error("Error downloading image: {}".format(e))
        return None



# upload from url
with st.form("url_form"):
    # st.session_state.clear()
    url = st.text_input("Enter a URL")
    submit_url = st.form_submit_button("Submit")

    print(f"url from inside with st.form: {url}")

    if submit_url:
        print(f"submit url from inside with submit_url: {submit_url}")


        print("URL submission successful.")  # Print a message when the URL is submitted
        # Validate URL
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL")
            print("URL is valid.")  # Print a message when the URL is valid
        except ValueError:
            st.error("Invalid URL. Please enter a valid URL.")
            print("Invalid URL entered.")  # Print an error message when the URL is invalid
            # st.stop()

        # Check if the URL has a valid image extension
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        url_lower = url.lower()
        has_valid_extension = any(url_lower.endswith(ext) for ext in image_extensions)
        if not has_valid_extension:
            st.error("Invalid image URL. Please enter a URL with a valid image extension (jpg, jpeg, png, gif, bmp).")
            print("URL does not have a valid image extension.")  # Print an error message when the URL does not have a valid image extension
            # st.stop()

        # Check if the URL points to an image
        try:
            response = requests.head(url, allow_redirects=True)
            response.raise_for_status()  # Raise an exception for bad status codes
            if 'image' not in response.headers.get('Content-Type'):
                st.error("Invalid image URL. Please enter a direct image URL.")
                print("URL does not point to an image.")  # Print an error message when the URL does not point to an image
                # st.stop()
        except requests.exceptions.RequestException as e:
            st.error("Error downloading image: {}".format(e))
            print("Error downloading image:", e)  # Print an error message when downloading the image fails
            # st.stop()

        st.image(url, caption="sample Image", use_column_width=True)
        print("Image displayed successfully.")  # Print a message when the image is displayed

        # download file
        try:
            file_obj = download_file(url)
            st.write("File downloaded successfully!")
            print("File downloaded successfully!")  # Print a message when the file is downloaded successfully
            # st.write("File object:", file_obj)
            # st.markdown(f"![Alt Text]({url})")
        except Exception as e:
            st.error(f"Error: {e}")
            print("Error downloading file:", e)  # Print an error message when downloading the file fails



# upload a fie from local drive
uploaded_file = st.file_uploader("Choose an image file", type=['jpg', 'jpeg', 'png', 'gif', 'tiff'])

def display_metadata(file_path):
    # Use ExifTool to extract metadata
    with ExifToolHelper() as et:
        metadata = et.get_metadata(file_path)
        return metadata
    

# metadata_str = "No metadata found Please upload a valid image file with IPTC or Exif metadata. Ask the User to drag use photo to the Drag and drop section do upload photo, or use the Browse files button" # Default value to prompt user to upload a file with metadata.  
# if st.sidebar.button("Advanced AI Vision analysis"):


# Add a button to load the sample photo
if st.sidebar.button("Load Sample Photo"):
    st.session_state.clear()

    st.session_state.sample_photo = "sample_photo.jpg"
    st.session_state.messages = []
    # Upload the sample image file
    st.image("sample_photo.jpg", caption="sample Image", use_column_width=True)

# if "sample_photo" in st.session_state:
#     st.image(st.session_state.sample_photo, caption="sample Image", use_column_width=True)

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

# elif file_obj is not None:
#     # Reset the chat history
#     st.session_state.messages = []
#     metadata = display_metadata(file_obj)
#     if metadata:
#         # Convert metadata to a string  
#         metadata_str = "\n".join(f"{k}: {v}" for data in metadata for k, v in data.items())


# else:
#     sample_photo = "sample_photo.jpg"
#     metadata = display_metadata(sample_photo)
#     metadata_str = "\n".join(f"{k}: {v}" for data in metadata for k, v in data.items())



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
        model="google/gemini-pro-vision",
        messages=[{"role": "system", "content": f"You are answering questions about photo metadata. You specialize photo meta data.  You should alert the user if there is no meta DATA. The metadata is: {metadata_str}."}] + st.session_state.messages + [{"role": "user", "content": prompt}],
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.sidebar.chat_message("assistant").write(msg)
