''' Functions for loading game data from the system. '''
import json
import os

import config

from games.decorators import retry_on_exception
from games.s3 import read_object
from games.utils import get_gamefile_listdir


@retry_on_exception(max_retries=3, delay=2)
def load_json(filepath):
    '''
    Loads a json file, either from the local system or S3, determined by the environment.

    Parameters
    ----------
    filepath : str
        The path to the file.

    Returns
    -------
    dict
        The data in the file.
    '''

    if config.ENV == 'DEV':
        with open(filepath, 'r') as f:
            return json.load(f)
    else:
        return json.loads(read_object(config.s3['data_bucket'], filepath))

@retry_on_exception(max_retries=3, delay=2)
def load_latest_file(game_id, type='full_text'):
    '''
    Loads the latest file from the system.

    Parameters
    ----------
    game_id : int
        The game id.
    type : str | 'full_text'
        The type of file to load (full_text or summaries).

    Returns
    -------
    dict
        The data in the file.
    '''

    file_path = os.path.join(config.file_save['path'], str(game_id), type)

    files = get_gamefile_listdir(file_path)

    if files:
        return load_json(os.path.join(file_path, files[-1]))

@retry_on_exception(max_retries=3, delay=2)
def load_history(game_id, summaries=False):
    '''
    Loads the history of the game from the system.

    Parameters
    ----------
    game_id : int
        The game id.
    summaries : bool | False
        If True, load the summaries, otherwise load the full text.
    '''

    type = 'summaries' if summaries else 'full_text'

    file_path = os.path.join(config.file_save['path'], str(game_id), type)

    history = []

    # load every file in the directory
    for file in get_gamefile_listdir(file_path):
        data = load_json(os.path.join(file_path, file))

        for item in data:
            history.append(item)

    return history


    

