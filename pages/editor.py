title="editor.py"
import streamlit as st
import numpy as np
import io
import os
from datetime import datetime
from PIL import Image
from exiftool import ExifToolHelper
from exiftool.exceptions import ExifToolException
import json


st.set_page_config(
    page_title="Image Metadata Viewer and Editor",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/omnisonic/chat_photo_history',
        'Report a bug': "https://github.com/omnisonic/chat_photo_history/issues",
        'About': "#  Upload an image to view and edit metadata!"
    }
)

# Create a Streamlit app
st.title("Image Metadata Editor (Always Required Fields Only)")

# Create a container at the top of the screen
error_container = st.container()

save_placeholder = st.empty()

# Initialize session state
if 'image_file' not in st.session_state:
    st.session_state.image_file = None
    st.session_state.image_data = None
    st.session_state.messages = []
    st.session_state.confirm_save = False
    st.session_state.updated_tags = {}
    st.session_state.show_download_button = False


unwritable_tags = [
    'SourceFile', 'ExifTool:ExifToolVersion', 'File:FileSize', 'File:FileAccessDate', 
    'File:FileInodeChangeDate', 'File:FileType', 'File:FileTypeExtension', 'File:MIMEType', 
    'File:CurrentIPTCDigest', 'File:ImageWidth', 'File:ImageHeight', 'File:EncodingProcess', 
    'File:BitsPerSample', 'File:ColorComponents', 'File:YCbCrSubSampling', 'JFIF:JFIFVersion', 
    'Photoshop:PhotoshopBGRThumbnail', 'Photoshop:PhotoshopFormat', 'XMP-mwg-rs:RegionAreaH', 
    'XMP-mwg-rs:RegionAreaW', 'XMP-mwg-rs:RegionAreaX', 'XMP-mwg-rs:RegionAreaY', 
    'APP14:DCTEncodeVersion', 'APP14:APP14Flags0', 'APP14:APP14Flags1', 'APP14:ColorTransform', 
    'Composite:ImageSize', 'Composite:Megapixels','File:FileName','File:Directory','File:FileModifyDate','File:FilePermissions','File:ExifByteOrder',
]

# Define Always Required fields
always_required_fields = {
    "Title": "Enter title",
    "Description": "Enter description",
    "Date Created": "YYYY:MM:DD",
    "Person in Image": "Enter person names",
    "Location Shown": "Enter location",
    "Location Name": "Enter location name",
    "GPS Longitude": "0.000000",
    "GPS Latitude": "0.000000"
}

# Display the uploaded image in the sidebar
with st.sidebar:
    # Get the image file from the user
    uploaded_file = st.file_uploader("Select an image file", type=["jpg", "jpeg"])

    # Only update session state if a new file is uploaded or cleared
    if uploaded_file is not None and uploaded_file != st.session_state.image_file:
        st.session_state.image_file = uploaded_file
        # When a new file is uploaded, also reset other relevant session states
        st.session_state.image_data = None # Clear old image data
        st.session_state.messages = []
        st.session_state.confirm_save = False
        st.session_state.updated_tags = {}
        st.session_state.show_download_button = False # Reset only on new upload
    elif uploaded_file is None and st.session_state.image_file is not None:
        # If uploaded_file becomes None (user cleared it) but session state still has one
        st.session_state.image_file = None
        st.session_state.image_data = None
        st.session_state.messages = []
        st.session_state.confirm_save = False
        st.session_state.updated_tags = {}
        st.session_state.show_download_button = False

    if st.session_state.image_file: # Only display image if it exists
        st.image(st.session_state.image_file, caption="Uploaded Image", use_column_width=True) # Use session state variable


if st.session_state.image_file is None:
    st.session_state.image_data = None
    st.warning("Please upload an image file to view and edit its metadata.")
else:
    # Convert the UploadedFile to bytes
    image_bytes = st.session_state.image_file.getvalue() # Use session state variable
    
    # Get original filename and extension
    original_name, extension = os.path.splitext(st.session_state.image_file.name)
    # Generate a unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{original_name}_metadata_updated_{timestamp}{extension}"
    file_path = unique_filename
    # file_path = f"./temp_{unique_filename}"
    with open(file_path, "wb") as f:
        f.write(image_bytes)

    # Create an ExifTool instance
    with ExifToolHelper() as et:
            try:
                # Get the metadata from the image
                metadata = et.get_metadata(file_path)
                
                # Create a form for each metadata tag
                form = st.form("Edit Metadata")
                form_fields = {}
                

                with form:
                    st.subheader("Edit Metadata Fields")
                    st.write("Edit the metadata values below:")
                    
                    # Create a dictionary for easier metadata lookup
                    metadata_dict = {}
                    for d in metadata:
                        metadata_dict.update(d)

                    # Define the exact ExifTool tags for the "Always Required" fields
                    # These are the keys that will be used for reading and writing metadata
                    required_exiftool_tags = {
                        "Title": "XMP:Title",
                        "Description": "XMP:Description",
                        "Date Created": "XMP:DateCreated", # Or EXIF:DateTimeOriginal
                        "Person in Image": "XMP:PersonInImage",
                        "Location Shown": "XMP:iptcExt:LocationShown",
                        "Location Name": "XMP:LocationShownLocationName",
                        "GPS Longitude": "XMP:LocationShownGPSLongitude", # Or GPS:GPSLongitude
                        "GPS Latitude": "XMP:LocationShownGPSLatitude" # Or GPS:GPSLatitude
                    }

                    for display_name, exiftool_tag in required_exiftool_tags.items():
                        # Get the current value from metadata_dict using the exiftool_tag
                        current_value = metadata_dict.get(exiftool_tag, always_required_fields.get(display_name, ""))
                        
                        # Special handling for DateCreated to prefer EXIF:DateTimeOriginal if available
                        if display_name == "Date Created" and "EXIF:DateTimeOriginal" in metadata_dict:
                            current_value = metadata_dict["EXIF:DateTimeOriginal"]

                        # Special handling for GPS coordinates to prefer GPS:GPSLongitude/Latitude if available
                        if display_name == "GPS Longitude" and "GPS:GPSLongitude" in metadata_dict:
                            current_value = metadata_dict["GPS:GPSLongitude"]
                        if display_name == "GPS Latitude" and "GPS:GPSLatitude" in metadata_dict:
                                current_value = metadata_dict["GPS:GPSLatitude"]

                        form_field = st.text_input(display_name, value=str(current_value), key=display_name)
                        form_fields[exiftool_tag] = form_field # Store with the actual exiftool tag for saving

                    # Save the changes
                    if st.form_submit_button("Save Changes"):
                        st.session_state.confirm_save = True
                        st.session_state.updated_tags = {}
                        for exiftool_tag, form_field_value in form_fields.items():
                            st.session_state.updated_tags[exiftool_tag] = form_field_value
                # End of form

                if st.session_state.get('confirm_save', False):
                    st.warning("Are you sure you want to save these changes? This will modify the image metadata.")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Confirm Save"):
                            try:
                                # Save the file with the unique filename
                                et.set_tags(file_path, tags=st.session_state.updated_tags, params=None)
                                st.session_state.confirm_save = False # Reset confirmation
                                st.session_state.show_download_button = True # Show download button

                            except ExifToolException as e:
                                error_container.error(f"""
                                        Error executing ExifTool: {e}""")
                                print(f" args ={e.args}") # more detail on errors
                                print(f" stderr ={e.stderr}") # more detail on errors
                    with col2:
                        if st.button("Cancel"):
                            st.session_state.confirm_save = False # Reset confirmation
                            st.session_state.show_download_button = False # Hide download button if cancelled

            except Exception as e:
                error_container.error(f"""
                                    args ={e.args}
                                    Error : {e}""")
                print(f" args ={e.args}") # more detail on errors
    
    # st.write(f"Debug: show_download_button = {st.session_state.get('show_download_button', 'not set')}")
    # Display download button if save was successful
    if st.session_state.get('show_download_button', False):
        # st.write("Debug: Inside download button block")
        st.success("Successfully updated metadata. You can now download the modified image.", icon="😁")
        # Define download_pressed locally or globally if needed elsewhere
        def download_pressed():
            st.success("Image Downloaded!", icon="😁") # This message will appear in the main area

        with open(file_path, "rb") as file:
            st.download_button(
                label="Download image",
                data=file,
                file_name=unique_filename,
                mime="image/jpg",
                on_click=download_pressed
            )
