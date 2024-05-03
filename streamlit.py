import streamlit as st
from exiftool import ExifToolHelper
from os import getenv
from openai import OpenAI
import pathlib
import requests
from io import BytesIO
from urllib.parse import urlparse
import tempfile
import mimetypes
import vision_func


api_key = getenv("OPENROUTER_API_KEY")

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




# UI for file uploader
st.title("AI CHAT with IPTC Metadata PHOTOS")

# Download file
file_obj = None

# Give a title
st.sidebar.header("Load From your Device")
uploaded_image = st.sidebar.file_uploader("Choose an image file", type=['jpg', 'jpeg', 'png', 'gif', 'tiff'])
if uploaded_image is not None:
    st.session_state.clear()

@st.cache_data
def get_file_from_url(url):
    headers = {'User-Agent': 'My Streamlit App (https://chat-photo-history.streamlit.app/)'}
    
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get the file extension from the response headers
        content_type = response.headers.get('Content-Type')
        file_ext = mimetypes.guess_extension(content_type)
        if not file_ext:
            file_ext = '.jpg'  # default to JPEG if no extension is found
        
        # Return the file contents as bytes
        return response.content, file_ext
    except requests.exceptions.RequestException as e:
        st.error("Error downloading image: {}".format(e))
        return None, None



@st.cache_data
def get_metadata(image_file):
    # Use ExifTool to extract metadata
    with ExifToolHelper() as et:
        metadata = et.get_metadata(image_file)
        print(f" inside get_metadata function ")
        return metadata


st.sidebar.header("Load From URl")

metadata_from_url_image_Outside = None
# upload from url
with st.sidebar.form("url_form"):

    url = st.text_input("Enter a URL")
    submit_url = st.form_submit_button("Submit")

    if submit_url:
        
        if uploaded_image is not None:
            uploaded_image.clear()

        st.session_state.clear()
        if "sample_photo" in st.session_state:
            del st.session_state.sample_photo

        
        print("URL submission successful.")

        # Validate URL
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL")
            print("URL is valid.")
        except ValueError:
            st.error("Invalid URL. Please enter a valid URL.")
            print("Invalid URL entered.")
            # st.stop()

        # Check if the URL has a valid image extension
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        url_lower = url.lower()
        has_valid_extension = any(url_lower.endswith(ext) for ext in image_extensions)
        if not has_valid_extension:
            st.error("Invalid image URL. Please enter a URL with a valid image extension (jpg, jpeg, png, gif, bmp).")
            print("URL does not have a valid image extension.")
            # st.stop()

        # Check if the URL points to an image
        try:
            response = requests.head(url, allow_redirects=True)
            response.raise_for_status()  # Raise an exception for bad status codes
            if 'image' not in response.headers.get('Content-Type'):
                st.error("Invalid image URL. Please enter a direct image URL.")
                print("URL does not point to an image.")
                # st.stop()
        except requests.exceptions.RequestException as e:
            st.error("Error downloading image: {}".format(e))
            print("Error downloading image:", e)
            # st.stop()

        # Download the image and get metadata
        try:
            file_contents, file_ext = get_file_from_url(url)
            if file_contents is not None:
                with tempfile.NamedTemporaryFile(suffix=file_ext) as temp_file:
                    temp_file.write(file_contents)
                    temp_file.seek(0)  # rewind the file pointer to the beginning
                    metadata = get_metadata(temp_file.name)
                    metadata_from_url_image_Outside = metadata
                    st.session_state.image_url = url
                    st.session_state.metadata_from_url_image_Outside = metadata_from_url_image_Outside
                    print("File downloaded successfully!")
            else:
                st.error("Failed to download image")
                print("Failed to download image")
        except Exception as e:
            st.error(f"Error: {e}")
            print("Error downloading file:", e)




# metadata_str = "No metadata found Please upload a valid image file with IPTC or Exif metadata. Ask the User to drag use photo to the Drag and drop section do upload photo, or use the Browse files button" # Default value to prompt user to upload a file with metadata.  
# if st.sidebar.button("Advanced AI Vision analysis


st.sidebar.header("Load A Sample with richly Embeded Metadata")

# Display a sample photo in the sidebar
st.sidebar.image("sample_photo.jpg", width=200)


sidebar_button_clicked = False
vision_response = ''
if st.sidebar.button("Load Sample Photo"):
    # st.image(None)
    sidebar_button_clicked = True
    uploaded_image = None
    st.session_state.sample_photo = "sample_photo.jpg"
    st.session_state.messages = []



# Create a reset button
if st.sidebar.button("Reset Everything"):
    st.session_state.clear()
    st.experimental_rerun()

sample_photo_metadata = None
if "sample_photo" in st.session_state:
    
    if "image_url" in st.session_state:
        del st.session_state.image_url
    if "uploaded" in st.session_state:    
        del st.session_state.uploaded_image
        st.experimental_rerun()  # Force Streamlit to re-run and update the UI

    print(f"""
            
            image_url deleted, line 148
            
            """)

    with open(st.session_state.sample_photo, "rb") as f:
        sample_image_data = f.read()
    st.sidebar.image(sample_image_data, caption="Sample Image", use_column_width=True)
    # Pass the sample_photo to the get_metadata function
    sample_photo_metadata = get_metadata(st.session_state.sample_photo)

# Display the persisted image and metadata
if "image_url" in st.session_state:

    st.sidebar.image(st.session_state.image_url, caption="Sample Image", use_column_width=True)


# else:
#     metadata_str = "No metadata found Please upload a valid image file with metadata. Ask the User to drag use photo to the Drag and drop section do upload photo, or use the Browse files button" # Default value to prompt user to upload a file with metadata.  




metadata_from_uploaded_image = None
if uploaded_image is not None:
    # Reset the chat history
    st.session_state.messages = []
    # Save the uploaded file to a temporary file to pass to ExifTool
    with open(uploaded_image.name, "wb") as f:
        f.write(uploaded_image.getbuffer())

    # Display the uploaded image
    st.sidebar.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    # Fetch and display the metadata

    metadata_from_uploaded_image = get_metadata(uploaded_image.name)
    if metadata_from_uploaded_image is not None:
        # Convert metadata to a string
        metadata_str = "\n".join(f"{k}: {v}" for data in metadata_from_uploaded_image for k, v in data.items())



print(f" meta data string from url image: {metadata_from_url_image_Outside}")


def get_current_metadata_variable():
    """
    Retrieves metadata from one of three possible sources: 
    metadata_from_url_image_Outside, sample_photo, or metadata_from_other_source.
    
    The function checks which of the three variables is not None and assigns its value to the metadata variable.
    If all variables are None, it displays an error message.
 
    Returns:
    metadata (dict): The metadata retrieved from one of the three sources.
    
    """
    if "metadata_from_url_image_Outside" in st.session_state:
        image_metadata = st.session_state.metadata_from_url_image_Outside
    # if metadata_from_url_image_Outside is not None:
    #     image_metadata = metadata_from_url_image_Outside
    elif metadata_from_uploaded_image is not None:
        image_metadata = metadata_from_uploaded_image
    elif sample_photo_metadata is not None:
        image_metadata = sample_photo_metadata

    else:
        image_metadata = None

    
    return image_metadata

# streamlit.py (255-293)


image_metadata = get_current_metadata_variable()

if sidebar_button_clicked:
    with st.spinner("Loading..."):
        if st.session_state.sample_photo is not None:
            image_path = st.session_state.sample_photo
            vision_response = vision_func.ai_vision(image_path, api_key)


print(f"the image_metadata before passed to request {type(image_metadata)}")


st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenRouter")

if "messages" not in st.session_state:
    st.session_state["messages"] = []



st.session_state["messages"].append({"role": "assistant", "content": vision_response})


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

prompt = st.chat_input("Ask a question...")

if prompt:
    if not getenv("OPENROUTER_API_KEY"):
        st.info("Please add your OpenRouter API key to environment variable OPENROUTER_API_KEY to continue.")
        st.stop()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(
        model="google/gemini-pro-vision",
        messages=[{"role": "system", "content": f"You are answering questions about photo metadata. You specialize photo meta data.  You should alert the user if there is no meta DATA. The metadata is: {image_metadata}."}] + st.session_state.messages + [{"role": "user", "content": prompt}],
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
