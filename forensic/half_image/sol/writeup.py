from PIL import Image
img = Image.open("flag.png").convert("RGB") 
width, height = img.size
left = img.crop((0, 0, width, height))
right = img.crop((hw, 0, width, height))
left.save("left.png")
rdata = right.tobytes()
with open("left.png", "rb") as fl: lp = fl.read()
with open("flag.png", "wb") as f_out:
    f_out.write(lp)
    f_out.write(rdata)

