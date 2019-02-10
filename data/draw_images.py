from PIL import Image

img = Image.open('menu_arrow.png')
img = img.resize((42, 30), Image.ANTIALIAS)
img.save('game_arrow42x30.png')
