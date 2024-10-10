# To process the training data, we will use the populated_processed_folder()
from pathlib import Path
import os
from tensor_hero.preprocessing.data import populate_processed_folder, populate_with_simplified_notes

unprocessed_path = Path.cwd() / 'Training Data' / 'Unprocessed'

processed_path = Path.cwd() / 'Training Data' / 'Processed'

'''
print("start")

processing_data = populate_processed_folder(unprocessed_data_path=unprocessed_path,
                                            processed_data_path=processed_path, PRINT_TRACEBACK=True, TRACK_PACKS=True)
'''

populate_with_simplified_notes(processed_path)