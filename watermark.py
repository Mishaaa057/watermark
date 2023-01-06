import os
from PIL import Image
from shutil import copytree

class Watermark:

    def __init__(self, watermark_path, target_folder, position=None, size=[], size_ptc=False, transparent_level=100):
        self.watermark_path = watermark_path
        self.target_folder = target_folder
        self.result_folder = None # TODO
        self.position = position 
        self.size = size
        self.size_ptc = size_ptc
        self.transparent_level = transparent_level
    

    def read_path(self, target_path, path_list=[]):
        
        for filename in os.listdir(target_path):
            filepath = os.path.join(target_path ,filename)

            if os.path.isdir(filepath):
                self.read_path(filepath, path_list)
            else:
                path_list.append(filepath)

        return path_list


    def load_watermark(self, path):
        # Prepare water mark, check for changes 
        watermark = Image.open(path)
        
        # Check if need to resize
        # Check for resize by pixels
        if self.size and not self.size_ptc:
            print("Resize by pixels")
            watermark = watermark.resize(self.size)

        # Check for resize by percantege
        elif not self.size and self.size_ptc:
            print("Resize by percantege")

            width, length = watermark.size
            new_width = int(width * (self.size_ptc/100))
            new_length = int(length * (self.size_ptc/100))

            watermark = watermark.resize((new_width, new_length))

        # Check if there no need to resize
        elif not self.size and not self.size_ptc:
            print("Do not resize")

        else:
            print("Wrong input!")
        
        # Check for transparent level
        if self.transparent_level < 100:
            # normal transparent level is 255 = 100%
            print("Change transparent level")
            new_transparent_level = int(255*(self.transparent_level / 100))
            watermark.putalpha(new_transparent_level)

        return watermark


    # Positions TR, TL, BR, BL / Top right, top left..
    def calculate_postion(self, watermark_size:list, target_image:Image, position="BL"):
        x, y = 0, 0

        x_size, y_size = watermark_size
        x_target_size, y_target_size = target_image.size
        
        if position == "TR":
            x = x_target_size - x_size

        elif position == "TL":
            x = 0
            y = 0
        
        elif position == "BR":
            x = x_target_size - x_size
            y = y_target_size - y_size
            
        
        elif position == "BL":
            y = y_target_size - y_size
            
        else:
            print("There no position")

        return x, y


    def run(self):
        print("Runing")
        # Create copy of files
        print("Creating copy of files...")
        copytree(self.target_folder, self.result_folder)


        # Get all file paths
        path_list = self.read_path(self.result_folder)
        for path in path_list:
            print(path)

        # Add watermark
        watermark = self.load_watermark(self.watermark_path)
        
        """# Check for result folder
        if os.path.basename(self.result_folder) not in os.listdir():
            print("Creating new result folder...")
            os.mkdir(self.result_folder)
        else:
            print("Result folder already exists")"""
        
        for image_path in path_list:
            # add watermark to each image
            im = Image.open(image_path)
            
            result_im = im.copy()
            
            # Calculate position of watermark on each image
            x_size, y_size = watermark.size
            x_pos, y_pos = self.calculate_postion([x_size, y_size], result_im)
            result_im.paste(watermark, (x_pos,y_pos), watermark)

            # Create new path for image with watermark
            result_path = os.path.join(self.result_folder, os.path.basename(image_path))
            result_im.save(image_path)

def main():
    mark = Watermark(watermark_path=r"C:\Users\Misha\Projects\watermark\sign.jpg",
            target_folder=r"C:\Users\Misha\Projects\watermark\target_images", size=[100,100], transparent_level=50)
    mark.result_folder=r"C:\Users\Misha\Projects\watermark\result"
    mark.run()

if __name__=="__main__":
    main()

    

