
from PIL import Image, ImageDraw, ImageFont
import os

font_list = ['Lobster', 'NeueMachina-Black', 'Docker_One']

class IProcessor:
    def __init__(self, user, img_url):
        self.img = img_url
        self.user = user


    def needsRotate(self):
        os.chdir(f"static/data/{self.user}")
        with Image.open(self.img) as i:
            os.chdir("../../..")
            if i.size[0] > i.size[1]:  
                return True
        
        return False


    def rotate(self):
        os.chdir(f"static/data/{self.user}")
        with Image.open(self.img) as i:
            os.chdir("../../..")
            out = i.rotate(270)
            print(self.img)
            # out.show()
            print("rotated")
            out.save(self.img)



    def add_text(self, text, font_name=font_list[0]):
        os.chdir(f"static/data/{self.user}")
        with Image.open(self.img) as i:
            draw_text = ImageDraw.Draw(i)

            w, h = i.size


            
        
            font = ImageFont.truetype(f"../../fonts/{font_name}.ttf", size = int(w/10))
            draw_text.text( 
                (w/2,h*0.9),
                font = font,
                anchor="mm",
                text = text,
                fill = ('white'),
                stroke_width=2,
                stroke_fill= 'black'

            )
            
            
            i.save(self.img)
            os.chdir("../../..")
            

    def black_n_white(self):
        os.chdir(f"static/data/{self.user}")
        with Image.open(self.img) as i:
            print(i.size)
            i.show()
            u = i.convert('1')
            w,h = i.size
            # u.show()
            print(u.size)
            
            u.save(self.img)
            os.chdir("../../..")












    

#a = IProcessor("static/images/dog_avatar_1.jpg")
#a.add_text("sample text", font_list[2])
#a.black_n_white()
