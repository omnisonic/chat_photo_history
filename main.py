import pyexiv2

# Open the image file
metadata = pyexiv2.ImageMetadata('image.jpg')

# Read the metadata from the file
metadata.read()

# Loop over each Exif, IPTC, and XMP key in the metadata
for key in metadata.exif_keys + metadata.iptc_keys + metadata.xmp_keys:
    # Print the key name and its associated value
    print(f'{key}: {metadata[key].raw_value}')

