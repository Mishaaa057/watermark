import os
import argparse
from PIL import Image
from shutil import copytree
from datetime import datetime


class Watermark:

    def __init__(self, watermark_path, target_folder_path, result_folder_path=None, 
                position=None, size=None, size_ptc=None, transparent_level=None):

        self.watermark_path = watermark_path
        self.target_folder_path = target_folder_path
        self.result_folder_path = result_folder_path
        self.position = position
        self.size = size
        self.size_ptc = size_ptc
        self.transparent_level = transparent_level

        self.valid_exstentions = [".png", ".jpg", ".webp", ".ppm",
                                ".tiff", ".gif", ".bmp"]
        self.valid_positions = ["BL", "BR", "TL", "TR"]
    
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
            #path_to_folder = os.path.dirname(self.result_folder_path)
            
            if os.path.isdir(self.result_folder_path):
                print("Path to result folder exists")
            else:
                print(f"[!] There is no such path for result folder \"{self.result_folder_path}\"")
                is_valid = False

        except Exception as err:
            print("[!] Unexpected problem occured while checking result folder path")
            print(err)
            is_valid = False


        # Check if position is valid
        # There 4 possible positions for watermark
        # BL - Bottom Left, BR - Bottim Right, TL - Top Left, TR - Top Right
        if self.position:
            if self.position not in self.valid_positions:
                print("[!] Wrong position entered")
                is_valid = False
            else:
                print("Watermark position is valid")
        else:
            print("Position not given, using Bottom Left corner")
            self.position = "BL"
        

        # Check if entered only one type of size pixels or percantage

        # Check for resize by pixels
        if self.size and not self.size_ptc:
            print("Change watermark size by pixels")

            # Check if entered size in pixels is valid
            try:
                if len(self.size) == 2:
                    self.size[0] = int(self.size[0])
                    self.size[1] = int(self.size[1])
                    print("Size in pixels is valid")
                else:
                    print("[!] Wrong size in pixels given")
                    is_valid = False
            except:
                print("[!] Unexpected problem occured while checking size in pixels")
                is_valid = False

        # Check for resize by percantege
        elif not self.size and self.size_ptc:
            print("Change watermark size by percantege")

            # Check if entered size in percantage is correct
            try:
                self.size_ptc = int(self.size_ptc)
                if self.size_ptc >= 1:
                    print("Size in percantage is valid")
                else:
                    print("[!] Size in percantage cannot be less than 1")
                    is_valid = False
            except:
                print("[!] Unexpected problem occured while checking size in percantage")
                is_valid = False

        # Check if there no need to resize
        elif not self.size and not self.size_ptc:
            print("Do not resize watermark")

        else:
            print("[!] Resize is not valid, please use only one resize method (by pixels or percantage)")
            is_valid = False
        
        # Check if transparent level is valid
        if self.transparent_level:
            try:
                self.transparent_level = int(self.transparent_level)
                if 1 <= self.transparent_level <= 100:
                    print("Transparent level is valid")
                else:
                    print("[!] Transparent level must be between 1 and 100")
                    is_valid = False
            except:
                print("[!] Unexpected problem occured while checking transparent level")
                is_valid = False
        else:
            print("Dont change transparent level")
            self.transparent_level = 100
        
        return is_valid
        

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
            watermark = watermark.resize(self.size)

        # Check for resize by percantege
        elif not self.size and self.size_ptc:
            width, length = watermark.size
            new_width = int(width * (self.size_ptc/100))
            new_length = int(length * (self.size_ptc/100))

            watermark = watermark.resize((new_width, new_length))

        # Check for transparent level
        if self.transparent_level < 100:
            # normal transparent level is 255 = 100%
            new_transparent_level = int(255*(self.transparent_level / 100))
            watermark.putalpha(new_transparent_level)
        else:
            # Dont change transparent level, set standard value
            watermark.putalpha(255)

        return watermark


    # Positions [TR, TL, BR, BL] in which corner watermark will be placed
    def calculate_postion(self, watermark_size:list, target_image:Image, position):
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
        if is_valid:
            print("Given data is valid")
        else:
            print("[!] Given wrong data, the program stops")
            exit()
        
        # Create copy of files
        print("Creating copy of files...")
        
        # Create path to result folder
        print("Name of folder with result images -", self.create_name())
        result_folder_with_name = os.path.join(self.result_folder_path, self.create_name())
        
        # Create result folder with raw images 
        print(self.target_folder_path, result_folder_with_name)
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
                x_pos, y_pos = self.calculate_postion([x_size, y_size], result_im, position=self.position)
                
                # Add watermark and save result image
                result_im.paste(watermark, (x_pos,y_pos), watermark)
                result_im.save(image_path)

                print(f"Added watermark to \"{os.path.basename(image_path)}\"")
            except:
                print(f"Unable to add watermark to \"{os.path.basename(image_path)}\"")


def built_arg_parser(descr):
    parser = argparse.ArgumentParser(descr)
    parser.add_argument("-wp", "--watermark_path", 
        help="Full path to watermark")

    parser.add_argument("-rp", "--result_path",
        help="Path where result folder should be created")

    parser.add_argument("-tp", "--target_path",
        help="Path to target folder with images")

    parser.add_argument("-p", "--position", metavar="BL",
        help="Position of corner for watermark (BL - Bottom Left, BR - Bottom Right, TL - Top Left, TR- Top Right )")

    parser.add_argument("-s", "--size", nargs=2, type=int, metavar="int",
        help="Size of watermark in pixels")

    parser.add_argument("-sp", "--size_percantage", type=int,
        help="Size of watermark in percantage ")

    parser.add_argument("-tl", "--transparent_level", type=int,
        help="Transparent level of watermark")

    return parser


def main():

    description = """
    Skript that adds watermark to each image in target folder
    User have to provide full path to watermark image, target folder and result folder
    """
    parser = built_arg_parser(description)
    args = parser.parse_args()

    # Check if any arguments given
    if any(vars(args).values()):
        mark = Watermark(watermark_path=args.watermark_path,
                result_folder_path=args.result_path,
                target_folder_path=args.target_path,
                position=args.position,
                size=args.size,
                size_ptc=args.size_percantage,
                transparent_level=args.transparent_level)
        mark.run()
        
    else:
        # If arguments not given show help and exit
        parser.print_help()


if __name__=="__main__":
    main()

    

