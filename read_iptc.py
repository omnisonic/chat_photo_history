from PIL import Image
image = Image.open('image.jpg')
iptc_info = image.getiptcinfo()
date_created = iptc_info.get('IPTC:DateCreated')
print(date_created)
