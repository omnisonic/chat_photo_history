import streamlit as st
from exiftool import ExifToolHelper

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
        for data in metadata:
            # Streamlit writes a dictionary in a nice format automatically
            st.write(data)
