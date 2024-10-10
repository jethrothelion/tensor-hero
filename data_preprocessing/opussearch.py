import os
import shutil

# Function to recursively search and delete directories containing .opus files
def delete_folders_with_opus(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for dirname in dirnames:
            dir_to_check = os.path.join(dirpath, dirname)
            if any(file.endswith('.opus') for file in os.listdir(dir_to_check)):
                print(f"Deleting folder: {dir_to_check}")
                shutil.rmtree(dir_to_check)
                print(f"Folder deleted: {dir_to_check}")

# Replace 'root_directory_path' with the path to the root directory where you want to start
root_directory_path = "Training Data/Unprocessed"

delete_folders_with_opus(root_directory_path)