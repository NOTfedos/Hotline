from PIL import Image

img = Image.open('ch_arrow.png')
img = img.resize((45, 26), Image.ANTIALIAS)
img.save('ch_arrow.png')
