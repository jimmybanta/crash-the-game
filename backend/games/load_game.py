import json
import os

import config

from games.decorators import retry_on_exception


@retry_on_exception(max_retries=3, delay=2)
def load_file(filepath):
    '''
    Loads a json file from the system.
    '''

    # TO DO - connect to s3, for stag and prod

    if config.ENV == 'DEV':
        with open(filepath, 'r') as f:
            return json.load(f)

@retry_on_exception(max_retries=3, delay=2)
def load_txt_file(filepath):
    '''
    Loads a txt file from the system.
    '''

    # TO DO - connect to s3, for stag and prod

    if config.ENV == 'DEV':
        with open(filepath, 'r') as f:
            return f.read()
        
@retry_on_exception(max_retries=3, delay=2)
def load_latest_file(game_id, type='full_text'):
    '''
    Loads the latest game from the system.
    '''

    file_path = f'{config.file_save["path"]}/{game_id}/{type}/'

    files = sorted(os.listdir(file_path))

    if files:
        return load_file(f'{file_path}/{files[-1]}')

@retry_on_exception(max_retries=3, delay=2)
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

@retry_on_exception(max_retries=3, delay=2)
def load_history_summary(game_id):
    '''
    Loads the summary history of the game from the system.
    '''
    
    file_path = f'{config.file_save["path"]}/{game_id}/summaries/'

    history = []

    for file in sorted(os.listdir(file_path)):
        if file.endswith('.json'):
            data = load_file(f'{file_path}/{file}')

            for item in data:
                history.append(item)

    return history

    

