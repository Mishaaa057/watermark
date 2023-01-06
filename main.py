from PIL import Image

#Create an Image Object from an Image
im = Image.open('target_images/img1.jpg')

sign = Image.open("sign.jpg")
sign.putalpha(128)

back_im = im.copy()
back_im.paste(sign, (10,10), sign)
back_im.show()

#Save watermarked image
im.save(r'C:\Users\Misha\Projects\watermark\target_images\test\watermark.jpg')