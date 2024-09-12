''' Contains functions for saving a game to the system. '''

import config
from pathlib import Path
import json
import os

from games.models import Game
from games.load_game import load_file

from games.decorators import retry_on_exception, catch_and_log


@retry_on_exception(max_retries=3, delay=2)
def save_file(filepath, data):
    '''
    Saves a file to the system.
    '''

    # TO DO - connect to s3, for stag and prod

    if config.ENV == 'DEV':
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

@catch_and_log
def save_text(game_id, new_data, turn=None,
              writer='ai', 
              save_type='append',
              type='full_text'):
    '''
    Saves game data to the system.

    Later on, we can implement type='summary' to save a summary of parts, to use for prompting.
    '''

    if type in ['full_text', 'summaries']:
        file_save_dir = f'{config.file_save["path"]}/{game_id}/{type}/'
    elif type == 'initialization':
        file_save_dir = f'{config.file_save["path"]}/{game_id}/'

    # create the directory if it doesn't exist
    # only need this for dev
    if config.ENV == 'DEV':
        Path(file_save_dir).mkdir(parents=True, exist_ok=True)

    if type in ['full_text', 'summaries']:
        # find the latest file
        files = sorted(os.listdir(file_save_dir))
        # if there are no files, then start at 0
        if not files:
            file_num = 0
            data = []
        else:
            # check how big the latest file is
            latest_file = files[-1]
            # if the file is too big, start a new file
            if os.path.getsize(f'{file_save_dir}/{latest_file}') > config.file_save['max_size']:
                file_num = int(latest_file.split('.')[0]) + 1
                data = []
            # otherwise, use the latest file
            else:
                file_num = int(latest_file.split('.')[0])
                # read the file
                data = load_file(f'{file_save_dir}/{file_num}.json')
            
        file_save_path = f'{file_save_dir}/{file_num}.json'
    elif type == 'initialization':
        file_save_path = f'{file_save_dir}/initialization.json'
        if os.path.exists(file_save_path):
            data = load_file(file_save_path)
        else:
            data = []
    
    if save_type == 'append':
        d = {'writer': writer, 'text': new_data}
        # add the turn data
        if turn is not None:
            d['turn'] = turn
        data.append(d)
    elif save_type == 'overwrite':
        data = new_data
    
    save_file(file_save_path, data)

    
     
@catch_and_log
def remove_turn(game_id, turn):
    ''' 
    Removes a turn from a game.
    This is necessary when an error occurs in the middle of a turn,
    and we need to rewind the game to the previous turn.
    '''

    # first, full text
    full_text_files = sorted(os.listdir(f'{config.file_save["path"]}/{game_id}/full_text/'))

    last_full_text_file = full_text_files[-1]

    full_text_data = load_file(f'{config.file_save["path"]}/{game_id}/full_text/{last_full_text_file}')

    # remove the turn
    new_full_text_data = [item for item in full_text_data if item['turn'] != turn]

    # save the new full text
    save_text(game_id, new_full_text_data, save_type='overwrite', type='full_text')
    
    # then, summaries
    summary_files = sorted(os.listdir(f'{config.file_save["path"]}/{game_id}/summaries/'))

    last_summary_file = summary_files[-1]

    summary_data = load_file(f'{config.file_save["path"]}/{game_id}/summaries/{last_summary_file}')

    # remove the turn
    new_summary_data = [item for item in summary_data if item['turn'] != turn]

    # save the new summaries
    save_text(game_id, new_summary_data, save_type='overwrite', type='summaries')