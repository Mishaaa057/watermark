import os
from PIL import Image
from shutil import copytree
from datetime import datetime


class Watermark:

    def __init__(self, watermark_path, target_folder_path, result_folder_path=None, 
                position=None, size=[], size_ptc=False, transparent_level=100):

        self.watermark_path = watermark_path
        self.target_folder_path = target_folder_path
        self.result_folder_path = result_folder_path # 
        self.position = position 
        self.size = size
        self.size_ptc = size_ptc
        self.transparent_level = transparent_level

        self.valid_exstentions = [".png", ".jpg", ".webp", ".ppm",
                                ".tiff", ".gif", ".bmp"]
    
    def get_curr_time(self):
        """
        Get current date and time in one string
        """
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d%H%M%S")
        return dt_string
    
    def create_name(self):
        """
        Create name for result folder
        where iamges with watermark will be stored
        """
        name = f"{self.get_curr_time()}"
        return name

    def is_data_valid(self):
        """
        Check if all given data is valid
        return: boolean 
        """

        is_valid = True
        
        # Check for watermark path and check is image is valid
        # Check path if file exists

        try:
            # Make raw string (to skip possible special signs)
            self.watermark_path = r"{}".format(self.watermark_path)
            
            if os.path.isfile(self.watermark_path):
                # Check if file with a proper extension
                ext = os.path.splitext(self.watermark_path)[-1]
                if ext in self.valid_exstentions:
                    print("Watermark is valid")
                else:
                    print("[!] Incorrect extention for watermark image")
                    is_valid = False

            else:
                print(f"[!] There is no such file with path \"{self.watermark_path}\"")
                is_valid = False

        except Exception as err:
            print("[!] Unexpected problem occured while checking watermark")
            print(err)
            is_valid = False
        
        # Check if target folder exists
        try:
            # Make raw string
            self.target_folder_path = r"{}".format(self.target_folder_path)

            if os.path.isdir(self.target_folder_path):
                print("Target folder exists")
            else:
                print(f"[!] There is no such folder with path \"{self.target_folder_path}\"")
                is_valid = False

        except Exception as err:
            print("[!] Unexpected problem occured while checking target folder path")
            print(err)
            is_valid = False

        # Check for result folder path
        try:
            # Make raw string
            self.result_folder_path = r"{}".format(self.result_folder_path)

            # Get and check path to directory where result folder shoud be created
            path_to_folder = os.path.dirname(self.result_folder_path)

            if os.path.isdir(path_to_folder):
                print("Path to result folder exists")
            else:
                print(f"[!] There is no such path for result folder\"{path_to_folder}\"")
                is_valid = False

        except Exception as err:
            print("[!] Unexpected problem occured while checking result folder path")
            print(err)
            is_valid = False



    def read_path(self, target_path, path_list=[]):
        """
        Get paths of all files in the directory recursively
        return:[str]
        """
        for filename in os.listdir(target_path):
            filepath = os.path.join(target_path ,filename)

            if os.path.isdir(filepath):
                self.read_path(filepath, path_list)
            else:
                path_list.append(filepath)

        return path_list


    def load_watermark(self, path):
        """ Load and prepare water mark, check for changes
            return: PIL.Image """
        watermark = Image.open(path)
        
        # Check if need to resize
        # Check for resize by pixels
        if self.size and not self.size_ptc:
            print("Change watermark size by pixels")
            watermark = watermark.resize(self.size)

        # Check for resize by percantege
        elif not self.size and self.size_ptc:
            print("Change watermark size by percantege")

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


    # Positions [TR, TL, BR, BL] in which corner watermark will be placed
    def calculate_postion(self, watermark_size:list, target_image:Image, position="BR"):
        """
        Function calculate position for watermark
        return: x, y
        Where x and y represents position for watermark in pixels
        """
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

        print("Checking if data is valid...")
        is_valid = self.is_data_valid()

        # Create copy of files
        print("Creating copy of files...")
        
        # Create path to result folder
        print("Name of folder with result images -", self.create_name())
        result_folder_with_name = os.path.join(self.result_folder_path, self.create_name())
        
        # Create result folder with raw images 
        copytree(self.target_folder_path, result_folder_with_name)


        # Get all file paths
        path_list = self.read_path(result_folder_with_name)

        # Add watermark
        watermark = self.load_watermark(self.watermark_path)

        
        for image_path in path_list:
            try:
                # add watermark to each image
                im = Image.open(image_path)
                
                result_im = im.copy()
                
                # Calculate position of watermark on each image
                x_size, y_size = watermark.size
                x_pos, y_pos = self.calculate_postion([x_size, y_size], result_im)
                
                # Add watermark and save result image
                result_im.paste(watermark, (x_pos,y_pos), watermark)
                result_im.save(image_path)

                print(f"Added watermark to \"{os.path.basename(image_path)}\"")
            except:
                print(f"Unable to add watermark to \"{os.path.basename(image_path)}\"")


def main():
    mark = Watermark(watermark_path=r"C:\Users\KUKUBIK\Projects\watermark\sign.jpg",
            result_folder_path=r"C:\Users\KUKUBIK\Projects\watermark",
            target_folder_path=r"C:\Users\KUKUBIK\Projects\watermark\target_images",
            size_ptc=50, transparent_level=50)
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
    
    """
    
    

if __name__=="__main__":
    main()

    

