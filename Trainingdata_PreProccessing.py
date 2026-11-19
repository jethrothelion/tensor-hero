import os
from pathlib import Path
import shutil
import subprocess
from pydub import AudioSegment
import gc

'''
This file fully prepares data for training. Make sure to back up all your songs before this if you want to play them aswell.
Recommended to run in order and also need to follow the Unprocessed Processed directory scheme
After this run Transformerdata_PreProccessing.py
'''

#CHANGE THIS MAYBE
training_path = Path(r'/run/media/jethr/14c35d99-a19c-4ff1-aef6-062f745f5d0e/linux keep/keep/Test trainign data/')
Unprocessed_directory_path = (training_path / "Unprocessed")

#MAY NEED TO CHANGE DEPENDING ON IF ITS SET AS A PATH VARIABLE OR NOT
FFMPEGPATH = r"ffmpeg"

#!!! CHANGE TO THE LOCATION OF YOUR MID2CHART APPLCATION
executable_path = Path(r"/home/jethr/Downloads/mid2chart/mid2chart.exe")

##!! CHANGE THIS POSSIBLY !!##
keep_midi = True

#deletes the files that were combined
delete_seperate_files = False


##1st Move all folders to top level ##note this needs to be refined, ESPICALLLY THE CHECK FOR DUPLICATE FOLDER

global count
global songcount
songcount = 0
count = 0


def delete_empty_folders(root_folder):
    for dirpath, dirnames, files in os.walk(root_folder, topdown=False):
        #Some song packs have unneeded information in .txts
        for f in files:
            if f.endswith('.txt'):
                full_path = os.path.join(dirpath, f)
                try:
                    os.remove(full_path)
                    print(f"Deleted file: {full_path}")
                except Exception as e:
                    print(f"Error deleting file {f}: {e}")


        ##WE CAN USE OS.RMDIR AS OUR CHECK FOR EMPTY DIRECTORYS AS ONLY WORKS IF DIRECTORY IS EMPTY
        try:
            os.rmdir(dirpath)
            print(f"Deleted empty folder: {dirpath}")
        except OSError:
            pass
        except Exception as e:
            print(f"Failed to delete error: {e}")

def move_folder(src_folder, dest_folder):
    """ Very specifically moves 1 folder and its contents to another place with a new name """

    src = Path(src_folder)
    dest = Path(dest_folder)
    global count


  # Handle duplicate names to prevent crashing
    target_path = dest / src.name

    #if the dirpath + name == original dir then it is a duplicate yk
    if target_path == src:
        return
    elif target_path.exists():
        print(f"Duplicate detected. Deleting buried copy: {src}")
        try:
            shutil.rmtree(src)
            print(f"removed buried {src} as is a duplicate")
            return
        except Exception as e:
            print(f"Error deleteing {src}: {e}")

    try:
        shutil.move(str(src), str(dest))
        print(f"Moved: {src} -> {dest}")
        count += 1

    except Exception as e:
        print(f"Error moving {src}: {e}")


def process_folders(base_folder):
    """
    Go through each folder till theres no more and then move those folders to the base folder

    Parameters:
    base_folder (str): The base folder which contains the folders to process.
    """
    global songcount

    for dirpath, dirnames, files in os.walk(base_folder, topdown=False):

        if any(str(filename).lower().endswith(('.chart', '.mid', '.midi')) for filename in files):
            songcount += 1

        #renamed for readability
        current_path = dirpath

        if current_path == base_folder:
            continue

        #if has no subdirectories
        if not dirnames:
            move_folder(dirpath, base_folder)

    #Preform a clean up pass to delete the now fully empty paths
    delete_empty_folders(base_folder)

if __name__ == "__main__":
    if Unprocessed_directory_path.exists():
        print(f"Processing: {Unprocessed_directory_path}")
        process_folders(Unprocessed_directory_path)
        print(f"Moved {count} folders")
        print(f"Found {songcount} songs")
    else:
        print(f"Path not found: {Unprocessed_directory_path}")
        exit()


##2nd Search for and convert any songs in opus format

global count
count = 0

# Function to recursively search and delete directories containing .opus files
def delete_folders_with_opus(root_dir):
    global count

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for file in filenames:
            if file.endswith('.opus'):
                file_path = os.path.join(dirpath, file)

                #0 grabs the root
                new_name = os.path.splitext(str(file))[0] + ".wav"
                output_path = os.path.join(dirpath, new_name)


                command = [FFMPEGPATH, '-i', str(file_path), '-vn' ,str(output_path)]
                try:
                    result = subprocess.run(command, capture_output=True, text=True)

                    if result.returncode == 0:
                        print(f"Done converting {file_path}")
                        count += 1
                        os.remove(file_path)
                    else:
                        print(f"{file} Conversion failed")
                except Exception as e:
                    print(f"An error eccored in converting to wav, {file_path}: {e}")

if __name__ == "__main__":
    delete_folders_with_opus(Unprocessed_directory_path)
    print(f"we converted {count} opus files")


##3rd Convert midi to clone hero .charts ##ADD CHECK IF GOES THROUGH

sucCount = 0

def run_exe_with_file(exe_path, file_path):
    """
    Runs an executable file, passing the specified file path as a command-line argument.

    Args:
        exe_path (str): The path to the executable (.exe) file.
        file_path (str): The path to the file you want to "drop" onto the exe.

    Returns True if the executable ran, False if it didnt
    """

    # Ensure paths are absolute and correctly formatted for the OS
    full_exe_path = os.path.abspath(exe_path)
    full_file_path = os.path.abspath(file_path)

    # The executable receives the file path as the first command-line argument
    command = [full_exe_path, full_file_path, '-m']
    print(f"Running command: {command}")
    try:
        result = subprocess.run(command, shell=False, capture_output=True, text=True)

        if result.stdout:
            print(result.stdout)

        if result.returncode != 0:
            print(f"Note: Executable closed with code {result.returncode}, but output should be fine.")

        print("Executable ran successfully.")
        print("-" * 20)
        return True

    except FileNotFoundError:
        print(f"Error: The executable was not found at {full_exe_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Executable failed with return code {e.returncode}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return False


count = 0
# Function to recursively search for midis in folders with no .chart and convert them
def search_for_midi(root_dir):
    global count
    global sucCount

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if any (filename.lower().endswith('.chart') for filename in filenames):
                continue
        for filename in filenames:
            ###!!NEED ADD CHECK FOR IF THERE IS .CHART AND .MIDI AND USE THE OG CHART

            if filename.lower().endswith(('.midi', '.mid')):
                count += 1

                # Construct the full path to the midi file
                full_file_path = os.path.join(dirpath, filename)

                # Run the exe with this specific file
                success = run_exe_with_file(executable_path, full_file_path)
                if success:
                    sucCount+=1
                if keep_midi == False:
                    os.remove(full_file_path)


if __name__ == "__main__":
    search_for_midi(Unprocessed_directory_path)
    print(f"There was {count} midi files without a chart that was attempted to be converted")
    print(f"{sucCount} successes")
    failCount = count - sucCount
    print(f"{failCount} failures")


##4th Layer sepperated songs

#!!!!! NEED CHANGE TO YOUR FFMPEG PATH
#os.environ["PATH"] += os.pathsep + r"D:\ffmpeg-2024-05-06-git-96449cfeae-essentials_build\bin"


def is_audio_file(filename):
    # This stops Python from reading invisible metadata files like '._guitar.ogg'.
    if filename.startswith('.'):
        return False
    return filename.lower().endswith(('.ogg', '.mp3', '.wav'))

count = 0

def layer_tracks(folder_path):
    global count


    for dirpath, dirnames, filenames in os.walk(folder_path, topdown=False):
        dir_path = Path(dirpath)
        audio_files = []
        guitar_files = []
        files_to_combine = []
        combined = None

        for file in filenames:
            if is_audio_file(file):
                if str(file).__contains__("combinned") or str(file).__contains__("preview"):
                    continue
                audio_files.append(dir_path / file)

                if 'guitar' in file.lower(): #or 'rhythm' in file.lower():
                    guitar_files.append(dir_path / file)

        if len(audio_files) == 0:
            continue

        # Decide which files to combine
        if len(audio_files) > 1:
            if len(guitar_files) > 1:
                files_to_combine = guitar_files
                print(f"Found {len(guitar_files)} guitar tracks: {[f.name for f in guitar_files]}, combining those")
            elif len(guitar_files) == 0 and len(audio_files) > 1 :
                files_to_combine = audio_files
                print(f"No guitar tracks found, combining all {len(audio_files)} audio files")
        else:
            print(f"Not enough audio files to combine in {dir_path}")
            continue

        if len(files_to_combine) != 0:
            print(f"Processing folder: {dir_path} ({len(files_to_combine)} audio files found)")

            try:
                combined = AudioSegment.from_file(str(files_to_combine[0]))
                for file in files_to_combine[1:]:
                    audio_segment = AudioSegment.from_file(str(file))
                    combined = combined.overlay(audio_segment)

                # Export the combined file #misspled on purpose not to be in the pervious list of files
                output_path = dir_path / 'combinned.ogg'
                combined.export(str(output_path), format="ogg")
                print(f"--> Saved combined file to: {output_path}")

                del combined
                if 'audio_segment' in locals():
                    del audio_segment

                ##Stop ffmpeg from lingering and stoping the download
                gc.collect()

                #Delete original files
                if delete_seperate_files == True:
                    for file in files_to_combine:
                        try:
                            os.remove(str(file))
                        except Exception as e:
                            print(f"Error in removing {file}: {e}")

                count += 1


            except Exception as e:
                print(f"Error processing {audio_files}: {e}")



if __name__ == "__main__":
    layer_tracks(Unprocessed_directory_path)
    print(f"we just layerd {count} tracks togeather")
