from pathlib import Path
import os
import sys
sys.path.insert(1, str(Path.cwd()))
from tensor_hero.preprocessing.data import populate_processed_folder, populate_with_simplified_notes, preprocess_transformer_data

'''
Run Trainingdata_PreProccessing.py first
Next Go to the Model folder and run one of the training files
'''

#change to current project directory !! SHOULD BE THE SAME AS training_path IN Trainingdata_PreProccessing.py
folder_path = Path(r"/run/media/jethr/14c35d99-a19c-4ff1-aef6-062f745f5d0e/linux keep/keep/Test trainign data/")


##5th Converts to spectrogram and put in new folder

'''
Takes raw, unprocessed data and processes expert .chart files into a specified processed folder
'''

# To process the training data, we will use the populated_processed_folder()
#repo_root = Path.cwd()
unprocessed_path = folder_path / 'Unprocessed'
processed_path = folder_path / 'Processed'

assert (os.path.isdir(unprocessed_path)), f'ERROR: Wrong directory: you should have a unprocessed folder in this directory({folder_path}) that is already cleaned up. make sure to run prior scripts'
if not os.path.isdir(processed_path):
    print("Creating Proccessed folder")
    os.makedirs(processed_path, exist_ok=True)

print('\nPOPULATING PROCESSED FOLDER WITH RAW DATA')
info = populate_processed_folder(unprocessed_path, processed_path, REPLACE_NOTES=False, PRINT_TRACEBACK=True)
print(info)


print('\nPOPULATING PROCESSED FOLDER WITH SIMPLIFIED NOTES')
populate_with_simplified_notes(processed_path)


##6th Splits songs into 4 second segmeants

'''
Once 1_preprocess_training_data.py has been run, this script will further process the data
to be ready for the transformer model.
'''

segment_length = 400
training_data_path = folder_path
#training_data_path = Path.cwd() / 'Training_Data' / 'Processed' / 'fully_curated'
train_val_test_probs = [0.95, 0.05, 0]

#folder to put model
model_training_directory_name = 'fully_curated_colab'
full_path = training_data_path / model_training_directory_name

if not os.path.exists(full_path):
    os.mkdir(full_path)


# # If training w/ colab:
# model_training_directory_name = 'colab_training_data'
# preprocess_transformer_data(segment_length,
                            # training_data_path,
                            # train_val_test_probs,
                            # model_training_directory_name,
                            # COLAB=True)

# If not training w/ colab:
# model_training_directory_name = 'colab_training_data'
# preprocess_transformer_data(segment_length,
                            # training_data_path,
                            # train_val_test_probs,
                            # model_training_directory_name,
                            # COLAB=True)

# For generating source separated colab data:
preprocess_transformer_data('spectrogram.npy',
                            segment_length,
                            training_data_path,
                            train_val_test_probs,
                            model_training_directory_name,
                            COLAB=True)
