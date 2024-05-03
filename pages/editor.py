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

# Read the JSON file containing the metadata tags and placeholders
with open('metadata_tags.json') as f:
    optional_metadata_tags = json.load(f)

# Create a Streamlit app
st.title("Image Metadata Editor")

# Create a container at the top of the screen
error_container = st.container()

download_button_container = st.container()

save_placeholder = st.empty()

# Get the image file from the user
image_file = st.file_uploader("Select an image file", type=["jpg", "jpeg"])

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

st.sidebar.header('Select Metadata to add to your uploaded Image file')


checked_metadata_tags = {}

# Loop through the metadata tags and create a new field for each one
for tag_key, placeholder in optional_metadata_tags.items():
    tag_key_display = tag_key.replace(":", " ")
    new_field_checkbox = st.sidebar.checkbox(tag_key_display) 
    if new_field_checkbox:
        new_field_value = st.text_input(tag_key_display, placeholder=placeholder)
        checked_metadata_tags[tag_key] = new_field_value




if image_file:
    # Convert the UploadedFile to bytes
    image_bytes = image_file.getvalue()
    
    # Generate a unique filename and save the file to a temporary location on disk
    unique_filename = f"{image_file.name}"
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
            # If the checkbox is checked, show the new field input fields


            for d in metadata:
                for k, v in d.items():
                    if k not in unwritable_tags:
                        if ":" in k:
                            k_display = k.replace(":", " ")
                        else:
                            k_display = k

                        if k.startswith("EXIF"):
                            form_field = st.text_input(k_display, value=v)
                        elif k.startswith("IPTC"):
                            form_field = st.text_area(k_display, value=v)
                        elif k.startswith("XMP"):
                            form_field = st.text_input(k_display, value=v)
                        elif k.startswith("XMP-mwg-rs"):
                            form_field = st.number_input(k_display, value=v)
                        else:
                            form_field = st.text_input(k_display, value=v)

                        form_fields[k] = form_field

            # Save the changes

            if form.form_submit_button("Save Changes"):
                
                updated_tags = {}
                for k, form_field in form_fields.items():
                    updated_tags[k] = form_field
                for k, form_filed in checked_metadata_tags.items():
                    updated_tags[k] = form_field
                try:
                    # Save the file with the unique filename
                    et.set_tags(file_path, tags=updated_tags, params=None)
                    download_button_container.success("Successfully updated metadata", icon="😁")
                    
                except ExifToolException as e:
                    error_container.error(f"""
                      
                                Error executing ExifTool: {e}""")
                    print(f" args ={e.args}") # more detail on errors
                    print(f" stderr ={e.stderr}") # more detail on errors

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

