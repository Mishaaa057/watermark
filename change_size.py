from PIL import Image

im = Image.open("sign.jpg")
resized = im.resize((10,1000))
#resized.show()

print(im.size) # Width, length
new_size = 200 # in percentege

def resize_pct(image, new_size): # image type PIL Image
    width, length = image.size
    new_width = int(width * (new_size/100))
    new_length = int(length * (new_size/100))

    resized = image.resize((new_width, new_length))
    #resized.show()

resize_pct(im, new_size)
if "None":
    print("ok")