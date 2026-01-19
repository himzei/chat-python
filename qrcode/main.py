import qrcode 

data = "https://www.google.com"

img = qrcode.make(data) 

img.save("qrcode.png")