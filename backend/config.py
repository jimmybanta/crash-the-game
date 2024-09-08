
import json
import os
import dotenv


# load environment variables and aws region
## this is necessary for when celery runs as a daemon
dotenv.load_dotenv()

# set environment
ENV = os.getenv('ENV')


# helper functions
""" def get_parameter(name, decrypt=False, env=ENV):
    '''Returns a parameter from the Parameter store.'''

    # retrieve value from parameter store
    return SSM.get_parameter(Name=f'/{env}/{name}',
                             WithDecryption=decrypt)['Parameter']['Value'] """

def set_value(name, decrypt=False, env=ENV):
    '''Returns a value from the environment or parameter store.'''
    if ENV == 'DEV':
        return os.getenv(name)
    """ elif env in ['STAG', 'PROD', 'ALL']: 
        return get_parameter(name, decrypt=decrypt, env=env)
    else:
        raise ValueError('Invalid environment.') """
    
def set_llm_value(name, decrypt=False, env=ENV):
    '''Returns a value for the LLM API the environment or parameter store.'''

    # get the llm provider
    provider = set_value('LLM_PROVIDER', decrypt=decrypt, env=env)

    return set_value(f'{provider}_{name}', decrypt=decrypt, env=env)



# use .env file for local development environment
if ENV == 'DEV':
    db_secrets = {
        'username': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }


## set configuration

database = {
    'name': set_value('DB_NAME', decrypt=True),
    'user': db_secrets['username'],
    'password': db_secrets['password'],
    'endpoint': set_value('DB_ENDPOINT', decrypt=True),
    'port': set_value('DB_PORT', decrypt=True)
}

llm = {
    'provider': set_value('LLM_PROVIDER'),
    'api_key': set_llm_value('API_KEY'),
    'model': set_llm_value('MODEL'),
}

file_save = {
    'path': set_value('FILE_SAVE_PATH'),
    'max_size': int(set_value('MAX_FILE_SIZE'))
}

game_intro = {
    'path': set_value('GAME_INTRO_PATH')
}