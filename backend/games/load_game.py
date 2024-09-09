import json
import os

import config



def load_file(filepath):
    '''
    Loads a file from the system.
    '''

    # TO DO - connect to s3, for stag and prod

    if config.ENV == 'DEV':
        with open(filepath, 'r') as f:
            return json.load(f)

def load_history(game_id):
    '''
    Loads the history of the game from the system.
    '''
    
    file_path = f'{config.file_save["path"]}/{game_id}/full_text/'

    history = []

    for file in sorted(os.listdir(file_path)):
        if file.endswith('.json'):
            data = load_file(f'{file_path}/{file}')

            for item in data:
                history.append(item)

    return history

    

