import qrcode 

data = "hello world" 

img = qrcode.make(data) 

img.save("qrcode.png") 