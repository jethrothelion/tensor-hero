import torch.cuda
#from tensor_hero.inference import full_song_prediction
from pathlib import Path
from tensor_hero.inference import  full_song_prediction
from tensor_hero.model import Transformer
import torch
import pickle
import json


song_dir = Path.cwd() / 'inference' / 'songs'
outfolder = Path.cwd() / 'inference' / 'generated_songs'
audio_file = song_dir / 'Libidine 8 - Nora Orlandi (youtube).ogg'
model_to_load = ('model13-1')
print(audio_file)


model_path = Path.cwd() / 'model' /'saved_models_backup' / model_to_load
with open(model_path / 'params.pkl', 'rb') as f:
    params = pickle.load(f)
def convert_paths_to_str(obj):
    if isinstance(obj, dict):
        return {k: convert_paths_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_paths_to_str(i) for i in obj]
    elif isinstance(obj, Path):
        return str(obj)
    else:
        return obj

params_str = convert_paths_to_str(params)
print(json.dumps(params_str, indent=4))

# We use these parameters to define the skeleton of the model, then load the weights into it
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'device = {device}')

# Model hyperparameters are derived from the params dictionary
trg_vocab_size = params['trg_vocab_size']
embedding_size = params['embedding_size']
num_heads = params['num_heads']
num_encoder_layers = params['num_encoder_layers']
num_decoder_layers = params['num_decoder_layers']
dropout = params['dropout']
max_len = params['max_trg_len']
forward_expansion = params['embedding_size']*params['forward_expansion']

model = Transformer(
    embedding_size,
    trg_vocab_size,
    num_heads,
    num_encoder_layers,
    num_decoder_layers,
    forward_expansion,
    dropout,
    max_len,
    device,
).to(device)  # Always send the model to the GPU

# Load the weights into the model
model.load_state_dict(torch.load(model_path / (str(model_to_load)+'.pt'), map_location=device))
print(model)

# We have to define some things for the .chart file so it's actually playable
# just some dummy metadata for now
song_metadata = {'Name' : 'model12',
                'Artist' : 'Forrest',       # Forrest is the honorary author of all of our output
                'Charter' : 'tensorhero',
                'Offset' : 0,
                'Resolution' : 192,
                'Genre' : 'electronic',
                'MediaType' : 'cd',
                'MusicStream' : 'song.ogg'}

_, raw_output = full_song_prediction(song_path = audio_file,
                         model=model,
                         device=device,
                         sos_idx=432,
                         max_len=500,
                         song_metadata=song_metadata,
                         outfolder=outfolder,
                         RETURN_RAW_OUTPUT=True)