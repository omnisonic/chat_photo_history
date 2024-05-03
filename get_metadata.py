from exiftool import ExifToolHelper

# exclude unwritable tags so that we don't get errors when writing back to the image file.
unwritable_tags = [
    'SourceFile', 'ExifTool:ExifToolVersion', 'File:FileSize', 'File:FileAccessDate', 
    'File:FileInodeChangeDate', 'File:FileType', 'File:FileTypeExtension', 'File:MIMEType', 
    'File:CurrentIPTCDigest', 'File:ImageWidth', 'File:ImageHeight', 'File:EncodingProcess', 
    'File:BitsPerSample', 'File:ColorComponents', 'File:YCbCrSubSampling', 'JFIF:JFIFVersion', 
    'Photoshop:PhotoshopBGRThumbnail', 'Photoshop:PhotoshopFormat', 'XMP-mwg-rs:RegionAreaH', 
    'XMP-mwg-rs:RegionAreaW', 'XMP-mwg-rs:RegionAreaX', 'XMP-mwg-rs:RegionAreaY', 
    'APP14:DCTEncodeVersion', 'APP14:APP14Flags0', 'APP14:APP14Flags1', 'APP14:ColorTransform', 
    'Composite:ImageSize', 'Composite:Megapixels'
]

with ExifToolHelper() as et:
    for d in et.get_metadata("image.jpg"):
        for k, v in d.items():
            if k not in unwritable_tags:
                print(f"{k} = {v}") 
