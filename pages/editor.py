title="editor.py"
import streamlit as st
import numpy as np
import io
from PIL import Image
from exiftool import ExifToolHelper
from exiftool.exceptions import ExifToolException
import uuid


# Create a Streamlit app
st.title("Image Metadata Editor")

# Create a container at the top of the screen
error_container = st.container()

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
            for d in metadata:
                for k, v in d.items():
                    if k not in unwritable_tags:
                        # Create a form field for the tag
                        if k.startswith("EXIF"):
                            field_type = st.text_input
                        elif k.startswith("IPTC"):
                            field_type = st.text_area
                        elif k.startswith("XMP"):
                            field_type = st.text_input
                        elif k.startswith("XMP-mwg-rs"):
                            field_type = st.number_input    
                        else:
                            field_type = st.text_input

                        form_field = field_type(k.replace(":", " "), value=v)# the colon in the data is causing part if the key name to be truncated do we replace it with a blank space.
                        form_fields[k] = form_field

            # Save the changes
            if form.form_submit_button("Save Changes"):
                updated_tags = {}
                for k, form_field in form_fields.items():
                    updated_tags[k] = form_field

                try:
                    # Save the file with the unique filename
                    et.set_tags(file_path, tags=updated_tags, params=None)
                    st.success("Successfully updated metadata")
                    
                except ExifToolException as e:
                    error_container.error(f"""
                                args ={e.args}
                                stderr ={e.stderr}
                                Error executing ExifTool: {e}""")
                    print(f" args ={e.args}") # more detail on errors
                    print(f" stderr ={e.stderr}") # more detail on errors

                try:
                    # Create a download button with the unique file name
                    st.markdown("#### Download Modified Image")
                    # streamilit download button
                    # Assuming file_path is the path to your temporary file
                    with open(file_path, "rb") as file:
                        btn = st.download_button(
                            label="Download image",
                            data=file,
                            file_name=unique_filename,  # You can choose a suitable file name
                            mime="image/jpg"  # Make sure to use the correct MIME type for your file
                        )
          
                        st.success("Changes saved and image downloaded!")

                except Exception as e:
                    error_container.error(f'after open file for downloading{e}')





        except Exception as e:
            error_container.error(f"""
                                args ={e.args}
                                Error : {e}""")
            print(f" args ={e.args}") # more detail on errors

