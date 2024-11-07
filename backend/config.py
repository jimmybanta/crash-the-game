''' Configuration for the application. '''

import os
import dotenv
import json
import boto3


# load environment variables
dotenv.load_dotenv()

# set environment
ENV = os.getenv('ENV')
REGION = os.getenv('AWS_REGION')

if not ENV:
    raise ValueError('Environment not set.')

if ENV != 'DEV':
    # if this is staging or production, set the client
    ## parameter store
    SSM = boto3.client('ssm', region_name=REGION)

# helper functions
def get_parameter(name, decrypt=False, env=ENV):
    '''Returns a parameter from the Parameter store.'''

    # retrieve value from parameter store
    return SSM.get_parameter(Name=f'/CRASH/{env}/{name}',
                             WithDecryption=decrypt)['Parameter']['Value']

def set_value(name, decrypt=False, env=ENV):
    '''
    Returns a value from the environment or parameter store.

    Parameters
    ----------
    name : str
        The name of the value to retrieve.
    decrypt : bool
        Whether to decrypt the value.
    env : str
        The environment to retrieve the value from.
    '''

    if ENV == 'DEV':
        return os.getenv(name)
    elif env in ['STAG', 'PROD', 'ALL']: 
        return get_parameter(name, decrypt=decrypt, env=env)
    else:
        raise ValueError('Invalid environment.')
    
def set_llm_value(name, decrypt=False, env=ENV):
    '''
    Returns a value for the LLM API from the environment or parameter store.

    Parameters
    ----------
    name : str
        The name of the value to retrieve.
    decrypt : bool
        Whether to decrypt the value.
    env : str
        The environment to retrieve the value from.
    '''

    # get the llm provider
    provider = set_value('LLM_PROVIDER', decrypt=decrypt, env=env)

    # format the value name
    return set_value(f'{provider}_{name}', decrypt=decrypt, env=env)



## set configuration

django = {
    'secret_key': set_value('DJANGO_SECRET_KEY', decrypt=True, env='ALL'),
}

database = {
    'name': set_value('DB_NAME', decrypt=True),
    'user': set_value('DB_USER', decrypt=True),
    'password': set_value('DB_PASSWORD', decrypt=True),
    'endpoint': set_value('DB_ENDPOINT', decrypt=True),
    'port': set_value('DB_PORT', decrypt=True)
}

llm = {
    'provider': set_value('LLM_PROVIDER'),
    'summarization_target_word_count': int(set_value('LLM_SUMMARIZATION_TARGET_WORD_COUNT', env='ALL')),
    'api_key': set_llm_value('API_KEY', decrypt=True),
    'model': set_llm_value('MODEL'),
    'prompts_path': set_value('PROMPTS_PATH', env='ALL'),
}

file_save = {
    'path': set_value('FILE_SAVE_PATH', env='ALL'),
    'max_size': int(set_value('MAX_FILE_SIZE', env='ALL')),
    'game_setup_path': set_value('GAME_SETUP_PATH', env='ALL'),
}

s3 = {
    'data_bucket': set_value('DATA_BUCKET'),
}

email = {
    'from_address': set_value('EMAIL_FROM_ADDRESS', env='ALL', decrypt=True),
    'to_address': set_value('EMAIL_TO_ADDRESS', env='ALL', decrypt=True),
    'endpoint': set_value('AWS_SES_EMAIL_ENDPOINT', env='ALL'),
    'region': set_value('AWS_SES_REGION', env='ALL')
}


## setup the random setup options
# lists of themes, timeframes, and details for if the user wants a random setup
with open(os.path.join(file_save['game_setup_path'], 'themes.txt')) as f:
    themes_data = f.read()
with open(os.path.join(file_save['game_setup_path'], 'timeframes.txt')) as f:
    timeframes_data = f.read()
with open(os.path.join(file_save['game_setup_path'], 'details.txt')) as f:
    details_data = f.read()

random_setup = {
    'themes': [item.strip() for item in themes_data.split('\n') if item],
    'timeframes': [item.strip() for item in timeframes_data.split('\n') if item],
    'details': [item.strip() for item in details_data.split('\n') if item]
}


# get the current version
with open('current_version.json') as f:
    current_version = json.load(f)['version']

game_version = current_version

print(f'Using model {llm["model"]} from provider {llm["provider"]}.')