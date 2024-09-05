''' Contains functions for saving a game to the system. '''

import config
from pathlib import Path
import json
import os

from games.models import Game


def save_file(filepath, data):
    '''
    Saves a file to the system.
    '''

    # TO DO - connect to s3, for stag and prod

    if config.ENV == 'DEV':
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)



def load_file(filepath):
    '''
    Loads a file from the system.
    '''

    # TO DO - connect to s3, for stag and prod

    if config.ENV == 'DEV':
        with open(filepath, 'r') as f:
            return json.load(f)
    

def save_text(game_id, text, writer='ai', type='full_text'):
    '''
    Saves text of a game to the system.

    Later on, we can implement type='summary' to save a summary of parts, to use for prompting.
    '''

    file_save_path = f'{config.file_save["path"]}/{game_id}/{type}/'

    # create the directory if it doesn't exist
    # only need this for dev
    if config.ENV == 'DEV':
        Path(file_save_path).mkdir(parents=True, exist_ok=True)

    # find the latest file
    files = sorted(os.listdir(file_save_path))
    # if there are no files, then start at 0
    if not files:
        file_num = 0
        data = []
    else:
        # check how big the latest file is
        latest_file = files[-1]
        # if the file is too big, start a new file
        if os.path.getsize(f'{file_save_path}/{latest_file}') > config.file_save['max_size']:
            file_num = int(latest_file.split('.')[0]) + 1
            data = []
        # otherwise, use the latest file
        else:
            file_num = int(latest_file.split('.')[0])
            # read the file
            data = load_file(f'{file_save_path}/{file_num}.json')
    
    data.append({'writer': writer, 'text': text})

    # save the file
    save_file(f'{file_save_path}/{file_num}.json', data)

    
     
    
    
    
    





    pass

