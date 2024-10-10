import torch.cuda
#from tensor_hero.inference import full_song_prediction
from pathlib import Path
from tensor_hero.inference import  full_song_prediction

song_dir = Path.cwd()
outfolder = Path.cwd() / 'test2' / 'generated'
audio_file = song_dir / 'Killer-Queen-_Remastered-2011_.ogg'
print(audio_file)

from tensor_hero.model import Transformer
import torch
import pickle

# We use these parameters to define the skeleton of the model, then load the weights into it
print(torch.cuda.is_available())
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'device = {device}')

model_path = Path.cwd() / 'model' / 'saved_models' / 'long_train'
with open(model_path / 'params.pkl', 'rb') as f:
    params = pickle.load(f)

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

_ = full_song_prediction(song_path = audio_file,
                         model=model,
                         device=device,
                         sos_idx=432,
                         max_len=500,
                         song_metadata=song_metadata,
                         outfolder=outfolder)