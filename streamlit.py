import streamlit as st
from exiftool import ExifToolHelper
from os import getenv
from openai import OpenAI
import requests
from urllib.parse import urlparse
import tempfile
import mimetypes
import vision_func 
import tempfile
from io import BytesIO



#Streamlit page configuration
st.set_page_config(page_title="AI CHAT with Metadata PHOTOS", layout="wide", initial_sidebar_state="expanded")

# st.write(st.session_state) 

header = st.container()
# two columns
col1, col2, = st.columns(2)


api_key = getenv("OPENROUTER_API_KEY")


css = '''
<style>
    [data-testid="stSidebar"]{
        min-width: 400px;
        max-width: 800px;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)


# initialize Download file
file_obj = None

if 'image' not in st.session_state:
    st.session_state.image = None

# initialize user_image_url
if 'user_image_url' not in st.session_state:
    st.session_state.user_image_url = None

# initialize uploaded_image
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None

# initialize metadata
if'metadata' not in st.session_state:
    st.session_state.metadata = None

# initialize vision_response
if 'vision_response' not in st.session_state:
    st.session_state.vision_response = None

# Initialize a unique key for the file uploader in the session state if it doesn't exist
if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0

with header:
    st.title("AI CHAT with IPTC Metadata PHOTOS")



# Assuming ExifToolHelper is from pyexiftool package

def get_metadata(image):
    try:
        # Use ExifTool to extract metadata
        with ExifToolHelper() as et:
            metadata = et.get_metadata(image)
            print(f"Metadata extracted successfully. frin exiftool {metadata}")
            return metadata
    except Exception as e:
        st.error(f"An error occurred while extracting metadata: {e}")
        return None


# @st.cache_data
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

st.sidebar.header("Load From your Device")
uploader = st.sidebar.file_uploader("Choose an image file", type=['jpg', 'jpeg', 'png', 'gif', 'tiff'], key=st.session_state["file_uploader_key"])
# st.write("\n Line ~96: Uploader:", uploader)
print(f" line 97 value of uploader  the variable assigned to file_uploader() {uploader} ")

if uploader:
    
    # st.session_state.clear()
    st.session_state.image = uploader # .name to get the relative path from the uploader object
    # st.session_state.metadata = None
    # st.session_state.vision_response = None
    st.session_state["file_uploader_key"] += 1
    st.rerun()
    print(f" \n line 101 value of st session_state image {st.session_state.image} ")




st.sidebar.header("Load From URL")
# upload from url
with st.sidebar.form("url_form"):

    url = st.text_input("Enter a URL")
    submit_url = st.form_submit_button("Submit")
    # st.write(submit_url)
    if submit_url:
  
        print(" line 109, URL form submission activated.")
        # st.session_state.metadata = None
        # st.session_state.vision_response = None
        # Validate URL
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL")
            print("line 116,  URL is valid.")
        except ValueError:
            st.error("Line: Invalid URL. Please enter a valid URL.")
            print("Line: Invalid URL entered.")
            # st.stop()

        # Check if the URL has a valid image extension
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        url_lower = url.lower()
        has_valid_extension = any(url_lower.endswith(ext) for ext in image_extensions)
        if not has_valid_extension:
            st.error("Invalid image URL. Please enter a URL with a valid image extension (jpg, jpeg, png, gif, bmp).")
            print("line 128: URL does not have a valid image extension.")
            # st.stop()

        # Check if the URL points to an image
        try:
            headers = {'User-Agent': 'My Streamlit App (https://chat-photo-history.streamlit.app/)'}

            response = requests.head(url, headers=headers, allow_redirects=True)
            response.raise_for_status()  # Raise an exception for bad status codes
            if 'image' not in response.headers.get('Content-Type'):
                st.error("Invalid image URL. Please enter a direct image URL.")
                print("line 139: URL does not point to an image.")
                # st.stop()
        except requests.exceptions.RequestException as e:
            st.error("Error downloading image: {}".format(e))
            print("Line 143: Error downloading image:", e)
            # st.stop()

        st.session_state.image = url   
        print(f" \n Line 150 session state image type: {type(st.session_state.image)}")  

    

# Create a reset button
if st.sidebar.button("Reset Everything"):
    st.session_state.clear()
    st.rerun()

with col1:    
    container = st.empty()

    with container:
        if st.session_state.image is None or st.session_state.image == "":
            print(" \n Line 163 session state image is no or empyt string ")
            
            st.image("sample_photo.jpg", caption="Sample Image", use_column_width=True)
        elif st.session_state.image:    
            st.image(st.session_state.image, caption="Uploaded Image", use_column_width=True)
 
    with st.spinner("Loading..."):
        if st.button("Submit to AI Vision Analysis", key="vision_submit"):
            # vision response for the sample image
            if st.session_state.image is None or st.session_state.image == "":
                vision_response = vision_func.ai_vision("sample_photo.jpg", api_key)
                print(f" \n line ~170 vision_response {vision_response}[:100]")
                st.session_state.vision_response = vision_response
                print(f" \n line ~176 after session state assiged {st.session_state.vision_response[:100]}") # use [:100] to see only the first 200 characters
                st.success('Success! Image Analyzed!', icon="✅")
                # st.write(vision_response)           
            else:
                # in this case the vision response will be either a url or a file path which both are handle by the ai_vision function
                print(f"line 170:  submit to ai vision button: {st.session_state.image}")
                vision_response = vision_func.ai_vision(st.session_state.image, api_key)
                st.session_state.vision_response = vision_response
                print(f" \n line ~176 after session state assiged {st.session_state.vision_response[:100]}") # use [:100] to see only the first 200 characters
                st.success('Success! Image Analyzed!', icon="✅")
                # st.write(vision_response)
    # get the meta data from the image
    with st.spinner("Loading..."):
        if st.button("Submit to Metadata Analysis", key="metadata-submit"):
            if 'uploadedfile' in str(st.session_state.image).lower(): # check substring to make sure this is a st uploader object
                # st.write(f" meta data button ha {st.session_state.image} ")
                uploaded_image = st.session_state.image
                # st.write(f"\n Line 185 meta data is type: {type(uploaded_image)} ")
                with open(uploaded_image.name, "wb") as f:
                    f.write(uploaded_image.getbuffer())
                    metadata = get_metadata(uploaded_image.name)
                    st.session_state.metadata = metadata
                    st.success('Success! Image Analyzed!', icon="✅")
                    # st.write(metadata)

            elif 'https://' in str(st.session_state.image).lower():
                print(f"Line 188: Image has https: {type(st.session_state.image)}")

                try:
                    file_contents, file_ext = get_file_from_url(url)
                    print(f"\n Line ~197:  get from url file content type: {type(file_contents)}")
                    # st.session_state.image = url
                    if file_contents is not None:
                        with tempfile.NamedTemporaryFile(suffix=file_ext) as temp_file:
                            temp_file.write(file_contents)
                            temp_file.seek(0)  # rewind the file pointer to the beginning
                            metadata = get_metadata(temp_file.name)
                        st.session_state.metadata = metadata
                        st.success('Success! Please use the chat to ask about the metadata', icon="✅")
                    else:
                        st.error("Line 202: Failed to download image")
                        print("Line 203: Failed to download image")
                except Exception as e:
                    st.error(f"Error: {e}")
                    print("Line 206: Error downloading file:", e)

            else:
                metadata = get_metadata("sample_photo.jpg")
                st.session_state.metadata = metadata
                st.success('Success! Please use the chat to ask about the metadata', icon="✅")

    if st.session_state.vision_response is not None:
        st.write(st.session_state.vision_response)
        

with header:
    st.caption("🚀 AI Powered Photo Tool by JCTECH ")

with col2:
    st.subheader("Chat with the photo🖼️")
    message_container = st.container(height=500)
    # st.caption("💬 Chat with the photo🖼️")


        # Add a header

    # Add a comment to initialize the messages list
    # Initialize the messages list

    prompt = st.chat_input("Ask a question...", key="chat_input")


    
    if "messages" not in st.session_state:
        st.session_state["messages"] = []  # Initialize an empty list for chat messages
        print(" Line ~250 session state messages initialized")

    if not st.session_state.messages:
   
            st.session_state.messages.append({"role": "assistant", "content": "Hello 👋"})
            st.session_state.messages.append({"role": "assistant", "content": "I am a photo analysis bot 🤖"})
            st.session_state.messages.append({"role": "assistant", "content": "Please add a Photo by using the left hand sidebar 😊"})
            st.session_state.messages.append({"role": "assistant", "content": "Then Submit Metadata Analysis Button or Vision Analysis Button to start! 😊"})

    for msg in st.session_state.messages:
        message_container.chat_message(msg["role"]).write(msg["content"])

    if prompt:

        if not getenv("OPENROUTER_API_KEY"):
            st.info("Please add your OpenRouter API key to environment variable OPENROUTER_API_KEY to continue.")
            st.stop()

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        st.session_state.messages.append({"role": "user", "content": prompt})
        message_container.chat_message("user").write(prompt)
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[{"role": "system", "content": f"You are answering questions about photo metadata and vision response data. You specialize photo meta data and photo analysis. The user can submit metadata and vision response for you to use in your responses to the user questions. If you dont have the vision resonse or metadata, ask the user to submit either the metadata or vision response. The will be the submited metadata from an image analyzed by exiftool {st.session_state.metadata}. When there is vision response data or metadata you can chat with the user about it. This will be the vision response received from gemini-pro-vision api with submit to ai analysis button: {st.session_state.vision_response} "}] + st.session_state.messages + [{"role": "user", "content": prompt}],
        )
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        message_container.chat_message("assistant").write(msg)

# Create a button to clear the chat

    chat_input = st.empty()

        

    clear_chat_button = st.button("Reset Chat", key="clear_chat")
    # Check if the button is clicked
    if clear_chat_button:
        # Clear the chat by removing all messages
        st.session_state.messages.clear()
        st.session_state.messages = []
        # st.cache.clear()
        st.rerun()
        st.succsesss("Chat cleared")

if st.session_state.vision_response:

    print(f" \n END OF PAGE {st.session_state.vision_response[:100]}") # use [:100] to see only the first 200
if st.session_state.metadata:    
    print(f" \n END OF PAGE {st.session_state.metadata[:100]}") # use [:100] to see only the first 200
# st.write(st.session_state) 
