from rembg import remove
import os
from PIL import Image


def remove_bg(img, user):
    
    os.chdir(f"static/data/{user}")
    with Image.open(img) as i:
        w,h = i.size
        # i.show()
        
        print("before: ", w, h)
        output = remove(i)
        
        output.show()
        print("after: ",output.size)
        
        new_name = img[:img.index('.')]+'.png'
        
        
        
        output.save(new_name)

        os.chdir("../../..")
    return new_name
