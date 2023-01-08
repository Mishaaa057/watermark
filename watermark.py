import os
from PIL import Image
from shutil import copytree


class Watermark:

    def __init__(self, watermark_path, target_folder, position=None, size=[], size_ptc=False, transparent_level=100):
        self.watermark_path = watermark_path
        self.target_folder = target_folder
        self.result_folder = None
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
            print("Resize watermark by pixels")
            watermark = watermark.resize(self.size)

        # Check for resize by percantege
        elif not self.size and self.size_ptc:
            print("Resize watermark by percantege")

            width, length = watermark.size
            new_width = int(width * (self.size_ptc/100))
            new_length = int(length * (self.size_ptc/100))

            watermark = watermark.resize((new_width, new_length))

        # Check if there no need to resize
        elif not self.size and not self.size_ptc:
            print("Do not resize watermark")

        else:
            print("Wrong input!")
            exit()
        
        # Check for transparent level
        if self.transparent_level < 100:
            # normal transparent level is 255 = 100%
            print("Change transparent level")
            new_transparent_level = int(255*(self.transparent_level / 100))
            watermark.putalpha(new_transparent_level)
        else:
            print("Do not change transparent level.")
            watermark.putalpha(255)

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
        print("Running")
        # Create copy of files
        print("Creating copy of files...")
        copytree(self.target_folder, self.result_folder)


        # Get all file paths
        path_list = self.read_path(self.result_folder)

        # Add watermark
        watermark = self.load_watermark(self.watermark_path)
        
        """# Check for result folder
        if os.path.basename(self.result_folder) not in os.listdir():
            print("Creating new result folder...")
            os.mkdir(self.result_folder)
        else:
            print("Result folder already exists")"""
        
        for image_path in path_list:
            try:
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
                print(f"Added watermark to \"{os.path.basename(image_path)}\"")
            except:
                print(f"Unable to add watermark to \"{os.path.basename(image_path)}\"")
                

def main():
    r"""
    mark = Watermark(watermark_path=r"C:\Users\Misha\Projects\watermark\sign.jpg",
            target_folder=r"C:\Users\Misha\Projects\watermark\target_images", size_ptc=50, transparent_level=50)
    mark.result_folder=r"C:\Users\Misha\Projects\watermark\result"
    mark.run()
    """

    # Ask user for data (path to target folder, path to watermark, etc.)

    watermark_path = ""
    target_folder = ""
    size = []
    size_ptc = 100
    transparent_level = 100
    result_folder_path = ""

    print("Enter data to add watermarks for images")
    
    while True:
        # Get path to watermark
        path = input("\nEnter path to watermark (etner 0 to exit): ")
        if path == "0":
            break

        path = r"{}".format(path)
        is_valid = os.path.isfile(path)
        #print("is valid:", is_valid)

        if is_valid:
            watermark_path = path
            break
        else:
            print("[!] There no such image with that path, please try again.")
    
    while True:
        # Get path to target folder with images
        path = input("\nEnter path to folder with images (etner 0 to exit): ")
        if path == "0":
            break
        
        path = r"{}".format(path)
        is_valid = os.path.isdir(path)

        if is_valid:
            target_folder = path
            break
        else:
            print("[!] There is no such folder with that path, please try again.")
    
    print("\n[i] Next arguments are optional, you may skip them by pressing [ENTER]")

    while True:
        # Get path to result folder
        print("\nEnter path fore result folder where new images will be saved,")
        print("if not given, folder will be created in same directory with this script")
        path = input("(to exit enter 0): ")
        if path == "0":
            break

        elif path == "":
            path = os.getcwd()
            path = os.path.join(path,"results")
            result_folder_path = path
            break

        else:
            path = r"{}".format(path)
            is_valid = os.path.isdir(path)

            if is_valid:
                name = input("Enter result folder name: ")
                path = os.path.join(path, name)
                result_folder_path = path
                break
            else:
                print("[!] There is no directory with that path, please try again.")
    

    while True:
        # Get size in pixels
        print("\nTo enter size in percatage, skip this one")
        input_size = input("Enter size in pixels or skip, separate by x (100x100)(etner 0 to exit): ")
        if input_size == "0":
            break
        elif input_size == "":
            break
        
        try:
            input_size = input_size.split("x")
            input_size[0] = int(input_size[0])
            input_size[1] = int(input_size[1])
            size = input_size
            size_ptc = False
            break
        except:
            print("[!] Wrong input, please try again.")
    
    if not size:
        while True:
            # Get size in percantage
            input_size = input("\nEnter size in percantage no less than 1 or skip (etner 0 to exit): ")
            if input_size == "0":
                break
            elif input_size == "":
                break
            
            try:
                input_size = int(input_size)
                if input_size >= 1:
                    size_ptc = input_size 
                    break
                else:
                    print("[!] Wrong input, please try again.")
            except:
                print("[!] Wrong input, please try again.")

    while True:
        # Get transparent level
        level = input("\nEnter transparent level between 1 and 100 (etner 0 to exit): ")
        if level == "0":
            break
        elif level == "":
            break
        
        try:
            level = int(level)
            if 1 <= level <= 100:
                transparent_level = level
                break
            else:
                print("[!] Wrong input, please try again.")
            
        except:
            print("[!] Wrong input, please try again.")

    print("Watermark -", watermark_path)
    print("Target folder -", target_folder)
    print("Result folder -", result_folder_path)
    print("Size -", size)
    print("Size in ptc -", size_ptc)
    print("Transparent level -", transparent_level)
    
    marking = Watermark(watermark_path=watermark_path, target_folder=target_folder,
        size=size, size_ptc=size_ptc, transparent_level=transparent_level)
    marking.result_folder = result_folder_path
    marking.run()


if __name__=="__main__":
    main()

    

