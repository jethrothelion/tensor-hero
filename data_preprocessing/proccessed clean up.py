import os
import shutil

def move_contents(src_folder, dest_folder):
    """
    Move all contents from src_folder to dest_folder and remove src_folder.
    
    Parameters:
    src_folder (str): The source folder where contents will be moved from.
    dest_folder (str): The destination folder where contents will be moved to.
    """
    for item in os.listdir(src_folder):
        source = os.path.join(src_folder, item)
        destination = os.path.join(dest_folder, item)
        shutil.move(source, destination)
    os.rmdir(src_folder)

def process_folders(base_folder):
    """
    Process all folders in base_folder to move contents of third level folders into their parent folders.
    
    Parameters:
    base_folder (str): The base folder which contains the folders to process.
    """
    # Iterate over first level folders (folder1)
    for folder1_item in os.listdir(base_folder):
        folder1_path = os.path.join(base_folder, folder1_item)
        if os.path.isdir(folder1_path):
            print("passed 1")
            # Iterate over second level folders (folder2)
            for folder2_item in os.listdir(folder1_path):
                
                folder2_path = os.path.join(folder1_path, folder2_item)
                if os.path.isdir(folder2_path):
                    print("passed 2" + folder2_path)
                    
                    move_contents(folder2_path, folder1_path)
                    # Iterate over third level folders (folder3)
                   
    
                            

# Example usage
base_folder = "D:/New folder (2)"  # Replace with the actual path to the base folder
process_folders(base_folder)  # Process the folders starting from the base folder
 