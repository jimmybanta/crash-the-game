''' Functions for saving a game to the system. '''

import json
import os
from pathlib import Path

import config

from games.decorators import retry_on_exception, catch_and_log
from games.load_game import load_json
from games.s3 import write_object
from games.utils import get_gamefile_listdir, get_file_size, check_file_exists


@retry_on_exception(max_retries=3, delay=2)
def save_json(filepath, data):
    '''
    Saves a json to the system.
    Either to local or s3, depending on the environment.

    Parameters
    ----------
    filepath : str
        The path to the file.
    data : dict
        The data to save.

    Returns
    -------
    None
    '''

    if config.ENV == 'DEV':
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    else:
        write_object(config.s3['data_bucket'], filepath, json.dumps(data).encode('utf-8'))

@catch_and_log
def save_text(game_id, new_data, turn=None,
              writer='ai', 
              save_type='append',
              type='full_text'):
    '''
    Saves game data to the system.

    Parameters
    ----------
    game_id : int
        The game id.
    new_data : dict
        The new data to save.
    turn : int | None
        The turn number.
    writer : str | 'ai'
        The writer of the data.
    save_type : str | 'append'
        Whether to append the data to the file or overwrite it.
    type : str | 'full_text'
        The type of data to save.

    Returns
    -------
    None
    '''

    if type in ['full_text', 'summaries']:
        file_save_dir = os.path.join(config.file_save['path'], str(game_id), type)
    elif type == 'initialization':
        file_save_dir = os.path.join(config.file_save['path'], str(game_id))

    # create the directory if it doesn't exist
    # only need this for dev
    if config.ENV == 'DEV':
        Path(file_save_dir).mkdir(parents=True, exist_ok=True)

    if type in ['full_text', 'summaries']:
        # get all the files
        files = get_gamefile_listdir(file_save_dir)
        # if there are no files, then start at 0
        if not files:
            file_num = 0
            data = []
            file_save_path = os.path.join(file_save_dir, f'{file_num}.json')
        else:
            # check how big the latest file is
            latest_file = files[-1]
            # if the file is too big, start a new file
            if get_file_size(os.path.join(file_save_dir, latest_file)) > config.file_save['max_size']:
                file_num = int(latest_file.split('.')[0]) + 1
                data = []
                file_save_path = os.path.join(file_save_dir, f'{file_num}.json')
            # otherwise, use the latest file
            else:
                file_save_path = os.path.join(file_save_dir, latest_file)
                data = load_json(file_save_path)
            
    elif type == 'initialization':
        file_save_path = os.path.join(file_save_dir, 'initialization.json')
        if check_file_exists(file_save_path):
            data = load_json(file_save_path)
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
    
    save_json(file_save_path, data)

@catch_and_log
def remove_turn(game_id, turn):
    ''' 
    Removes a turn from a game.
    This is necessary when an error occurs in the middle of a turn,
    and we need to rewind the game to the previous turn.

    Parameters
    ----------
    game_id : int
        The game id.
    turn : int
        The turn to remove.

    Returns
    -------
    None
    '''

    ## first, full text
    # get the full text files
    full_text_files = get_gamefile_listdir(os.path.join(config.file_save['path'], str(game_id), 'full_text'))
    
    # if there are no files, then return
    try:
        last_full_text_file = full_text_files[-1]
    except IndexError:
        return

    # load the last full text file
    full_text_data = load_json(os.path.join(config.file_save['path'], str(game_id), 'full_text', last_full_text_file))
        
    # remove the turn
    new_full_text_data = [item for item in full_text_data if item['turn'] != turn]

    # save the new full text
    save_text(game_id, new_full_text_data, save_type='overwrite', type='full_text')
    

    ## then, summaries
    # get the summary files
    summary_files = get_gamefile_listdir(os.path.join(config.file_save['path'], str(game_id), 'summaries'))

    # if there are no files, then return
    try:
        last_summary_file = summary_files[-1]
    except IndexError:
        return

    # load the last summary file
    summary_data = load_json(os.path.join(config.file_save['path'], str(game_id), 'summaries', last_summary_file))

    # remove the turn
    new_summary_data = [item for item in summary_data if item['turn'] != turn]

    # save the new summaries
    save_text(game_id, new_summary_data, save_type='overwrite', type='summaries')