from torch.utils import tensorboard
from model import *
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
import os
import json
import pickle


# control the parameters of the run here
params = {
    'training_data' : 'random',
    'model_name' : 'model6',
    'optimizer' : 'Adam',

    'num_epochs' : 10,
    'batch_size' : 16,
    'shuffle' : True,
    'num_workers' : 4,
    'drop_last' : True,

    'max_trg_len' : 500,
    'max_src_len' : 500,
    'trg_vocab_size' : 435,
    'pad_idx' : 434,
    'embedding_size' : 512,

    'lr' : 3e-4,
    'num_heads' : 8,
    'num_encoder_layers' : 2,
    'num_decoder_layers' : 2,
    'dropout' : 0.1,
    'forward_expansion' : 4,

    'date' : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
}


# ---------------------------------------------------------------------------- #
#                              STORAGE PARAMETERS                              #
# ---------------------------------------------------------------------------- #

# create folder for model
override = False
if os.path.isdir(Path.cwd() / 'Model_1' / 'saved models' / params['model_name']):
    new_name = input('Directory already exists.\nEnter new model name or override with \'o\': ')
    if new_name == 'o':
        override = True
        # Use the description from last time
        with open(str(Path.cwd() / 'Model_1' / 'saved models' / params['model_name'] / 'params.pkl'), 'rb') as f:
            old_params = pickle.load(f)
        f.close()
        params['experiment_description'] = old_params['experiment_description']
    else:
        params['model_name'] = str(new_name)

# make directory for model and create model_file name
if not override:
    os.mkdir(Path.cwd() / 'Model_1' / 'saved models' / params['model_name'])

params['model_file_name'] = params['model_name'] + '.pt'
model_outfile = Path.cwd() / 'Model_1' / 'saved models' / params['model_name'] / params['model_file_name']
writer = SummaryWriter(r'runs/'+params['model_name'])

# ---------------------------------------------------------------------------- #
#                            EXPERIMENT DESCRIPTION                            #
# ---------------------------------------------------------------------------- #


# Validate parameters
print(json.dumps(params, indent=4))
response = str(input('Are the parameters correct (y/n)?: ')).lower()
while response not in ['y', 'n']:
    print('invalid input')
    response = str(input('Are the parameters correct (y/n)?: ')).lower()
if response == 'n':
    raise SystemExit(0)

# Gather description of experiment from user
if not override:
    experiment_description = input('Enter experiment description: ')
    params['experiment_description'] = experiment_description

# Save parameters
with open(str(Path.cwd() / 'Model_1'/ 'saved models' / params['model_name'] / 'params.pkl'), 'wb') as f:
    pickle.dump(params, f)
f.close()
print('parameters saved\n')


# ---------------------------------------------------------------------------- #
#                               MODEL PARAMETERS                               #
# ---------------------------------------------------------------------------- #

# NOTE: max_trg_len <= max_src_len otherwise side asset error is triggered
max_trg_len = params['max_trg_len'] # length of all target note sequences, holds 99 notes max
max_src_len = params['max_src_len']
pad_idx = params['pad_idx']

# DataLoader parameters
dl_params = {
    'batch_size' : params['batch_size'],
    'shuffle' : params['shuffle'],
    'num_workers' : params['num_workers'],
    'drop_last' : params['drop_last'],
}

# Define data loaders
train_path = Path(r'X:\Training Data\Model 1 Training\train')
# train_data = LazierDataset(train_path, max_src_len, max_trg_len, pad_idx)
train_data = RandomInputDataset(train_path, max_src_len, max_trg_len, pad_idx)
train_loader = torch.utils.data.DataLoader(train_data, **dl_params)
# val_path = Path(r'X:\Training Data\Model 1 Training\val')
# val_data = LazierDataset(val_path, max_src_len, max_trg_len, pad_idx)
# val_loader = torch.utils.data.DataLoader(val_data, **dl_params)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Training hyperparameters
learning_rate = params['lr']
batch_size = params['batch_size']

# Model hyperparameters
trg_vocab_size = params['trg_vocab_size']  # <output length>
embedding_size = params['embedding_size']
num_heads = params['num_heads']
num_encoder_layers = params['num_encoder_layers']
num_decoder_layers = params['num_decoder_layers']
dropout = params['dropout']
max_len = max_src_len
forward_expansion = params['embedding_size']*params['forward_expansion']

step = 0  # how many times the model has gone through some input

# Define model
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
).to(device)

# torch.save(model.state_dict(), 'model.pt')
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# criterion = nn.CrossEntropyLoss() # Multi-class loss, when you have a many class prediction problem
criterion = nn.CrossEntropyLoss(ignore_index=params['pad_idx'])

num_epochs = params['num_epochs']
model.train() # Put model in training mode, so that it knows it's parameters should be updated
for epoch in range(num_epochs):
    for batch_idx, batch in enumerate(train_loader):
        # Batches come through as a tuple defined in the return statement __getitem__ in the Dataset
        spec, notes = batch[0].to(device), batch[1].to(device)

        # forward prop
        output = model(spec, notes[..., :-1]) # Don't pass the last element into the decoder, want it to be predicted
        # print('output shape : {}'.format(output.shape))
        # output = output.reshape(-1, output.shape[2]) # Reshape the output for use by criterion
        notes = notes[..., 1:] # .reshape(-1)           # Same for the notes
        # print('notes shape 2 {}'.format(notes.shape))
        optimizer.zero_grad()                        # Zero out the gradient so it doesn't accumulate

        loss = criterion(output.permute(0,2,1), notes)     # Calculate loss, this is output vs ground truth
        loss.backward()                     # Compute loss for every node in the computation graph

        # This line to avoid the exploding gradient problem
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1)

        optimizer.step()    # Update model parameters
        writer.add_scalar("Training Loss", loss, global_step=step)
        step += 1

        if batch_idx%25 == 0:
            print('\nEpoch {}, Batch {}'.format(epoch+1,batch_idx))
            print('Training Loss: {}'.format(loss.item()))
        
        # if batch_idx%100 == 0:
            # print('Ground Truth (sample) : {}'.format(notes[0]))
            # print('Canidate (sample)     : {}'.format(torch.argmax(output[0], dim=1)))
        

    print(f'\nEpoch {epoch+1}/{num_epochs}')
    print(f'Training Loss: {loss.item()}')
    torch.save(model.state_dict(), str(model_outfile))
    print('model saved')
    # # Evaluate on validation set
    # model.eval()
    # for batch_idx, batch in enumerate(val_loader):
        # spec, notes = batch[0].to(device), batch[1].to(device)

        # # forward prop
        # output = model(spec, notes[..., :-1]) # Don't pass the last element into the decoder, want it to be predicted

        # # output = output.reshape(-1, output.shape[2]) # Reshape the output for use by criterion
        # notes = notes[..., 1:] # .reshape(-1)           # Same for the notes
        
        # loss = criterion(output.permute(0,2,1), notes)     # Calculate loss, this is output vs ground truth

        # writer.add_scalar("Validation Loss", loss, global_step=step)
        # step += 1
    # print('Validation Loss: {}'.format(loss.item()))

