import qrcode

img = qrcode.make("R01. 00100A")
type(img)  # qrcode.image.pil.PilImage
img.save("some_file.png")