title="editor.py"
import streamlit as st
import numpy as np
import io
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

download_button_container = st.container()

save_placeholder = st.empty()

# Initialize session state
if 'image_file' not in st.session_state:
    st.session_state.image_file = None
    st.session_state.image_data = None
    st.session_state.messages = []
    st.session_state.confirm_save = False
    st.session_state.updated_tags = {}

# Get the image file from the user
uploaded_file = st.file_uploader("Select an image file", type=["jpg", "jpeg"])

# Only update session state if a new file is uploaded
if uploaded_file is not None:
    st.session_state.image_file = uploaded_file
    # When a new file is uploaded, also reset other relevant session states
    st.session_state.image_data = None # Clear old image data
    st.session_state.messages = []
    st.session_state.confirm_save = False
    st.session_state.updated_tags = {}

if st.session_state.image_file is None:
    st.session_state.image_data = None
    st.warning("Please upload an image file")

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


# Create a sidebar with a checkbox to toggle the new field input
# show_new_field_input = st.sidebar.checkbox("Add New Field")

# Define Always Required fields
always_required_fields = {
    "XMP-dc:Title": "Enter title",
    "XMP-dc:Description": "Enter description",
    "XMP-photoshop:DateCreated": "YYYY:MM:DD",
    "XMP-IptcExtPersoninImage": "Enter person names",
    "XMP-iptcExt:LocationShown": "Enter location",
    "XMP-iptcExtLocationShown.locationName": "Enter location name",
    "GPS:GPSLongitude": "0.000000",
    "GPS:GPSLatitude": "0.000000"
}

if st.session_state.image_file: # Changed from 'if image_file:'
    # Convert the UploadedFile to bytes
    image_bytes = st.session_state.image_file.getvalue() # Use session state variable
    
    # Generate a unique filename and save the file to a temporary location on disk
    unique_filename = f"{st.session_state.image_file.name}" # Use session state variable
    file_path = unique_filename
    # file_path = f"./temp_{unique_filename}"
    with open(file_path, "wb") as f:
        f.write(image_bytes)

    # Display the uploaded image in the sidebar
    with st.sidebar:
        st.image(st.session_state.image_file, caption="Uploaded Image", use_column_width=True) # Use session state variable
    
    # Create an ExifTool instance
    with ExifToolHelper() as et:
        try:
            # Get the metadata from the image
            metadata = et.get_metadata(file_path)
            
            # Create a form for each metadata tag
            form = st.form("Edit Metadata")
            form_fields = {}
            
            # The redundant block below is removed.
            # Store image data in session state only if file is valid
            # if st.session_state.image_file is not None:
            #     st.session_state.image_data = image_bytes
            #     st.session_state.messages = []  # Reset messages on new image
            #     # Reset confirmation state for new image
            #     st.session_state.confirm_save = False
            #     st.session_state.updated_tags = {}
            # else:
            #     st.session_state.image_data = None
            #     error_container.error("No valid image file uploaded")

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
                    "XMP-dc:Title": "XMP:Title",
                    "XMP-dc:Description": "XMP:Description",
                    "XMP-photoshop:DateCreated": "XMP:DateCreated", # Or EXIF:DateTimeOriginal
                    "XMP-IptcExtPersoninImage": "XMP:PersonInImage",
                    "XMP-iptcExt:LocationShown": "XMP-iptcExt:LocationShown",
                    "XMP-iptcExtLocationShown.locationName": "XMP:LocationShownLocationName",
                    "GPS:GPSLongitude": "XMP:LocationShownGPSLongitude", # Or GPS:GPSLongitude
                    "GPS:GPSLatitude": "XMP:LocationShownGPSLatitude" # Or GPS:GPSLatitude
                }

                for display_name, exiftool_tag in required_exiftool_tags.items():
                    k_display = display_name.replace(":", " ")
                    
                    # Get the current value from metadata_dict using the exiftool_tag
                    current_value = metadata_dict.get(exiftool_tag, always_required_fields.get(display_name, ""))
                    
                    # Special handling for DateCreated to prefer EXIF:DateTimeOriginal if available
                    if display_name == "XMP-photoshop:DateCreated" and "EXIF:DateTimeOriginal" in metadata_dict:
                        current_value = metadata_dict["EXIF:DateTimeOriginal"]

                    # Special handling for GPS coordinates to prefer GPS:GPSLongitude/Latitude if available
                    if display_name == "GPS:GPSLongitude" and "GPS:GPSLongitude" in metadata_dict:
                        current_value = metadata_dict["GPS:GPSLongitude"]
                    if display_name == "GPS:GPSLatitude" and "GPS:GPSLatitude" in metadata_dict:
                        current_value = metadata_dict["GPS:GPSLatitude"]

                    form_field = st.text_input(k_display, value=str(current_value), key=display_name)
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
                            download_button_container.success("Successfully updated metadata", icon="😁")
                            st.session_state.confirm_save = False # Reset confirmation
                        except ExifToolException as e:
                            error_container.error(f"""
                                    Error executing ExifTool: {e}""")
                            print(f" args ={e.args}") # more detail on errors
                            print(f" stderr ={e.stderr}") # more detail on errors
                with col2:
                    if st.button("Cancel"):
                        st.session_state.confirm_save = False # Reset confirmation

            try:
                # Create a download button with the unique file name
                download_button_container.markdown("#### Download Modified Image")
                # streamilit download button
                # Assuming file_path is the path to your temporary file
                def download_pressed():
                    download_button_container.success("Image Downloaded!", icon="😁")

                with open(file_path, "rb") as file:
                    btn = download_button_container.download_button(
                        label="Download image",
                        data=file,
                        file_name=unique_filename,  # You can choose a suitable file name
                        mime="image/jpg",  # Make sure to use the correct MIME type for your file
                        on_click=download_pressed
                    )
            except Exception as e:
                error_container.error(f'after open file for downloading{e}')





        except Exception as e:
            error_container.error(f"""
                                args ={e.args}
                                Error : {e}""")
            print(f" args ={e.args}") # more detail on errors
