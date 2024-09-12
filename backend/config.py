''' Configuration settings for the application. '''

import os
import dotenv
import json
import boto3

from games.load_game import load_txt_file


# load environment variables and aws region
## this is necessary for when celery runs as a daemon
dotenv.load_dotenv()

# set environment
ENV = os.getenv('ENV')
REGION = os.getenv('AWS_REGION')

if not ENV:
    raise ValueError('Environment not set.')

if ENV != 'DEV':
    # if this is staging or production, set clients
    ## parameter store
    SSM = boto3.client('ssm', region_name=REGION)
    # secrets manager
    SM = boto3.client('secretsmanager', region_name=REGION)


# helper functions
def get_parameter(name, decrypt=False, env=ENV):
    '''Returns a parameter from the Parameter store.'''

    # retrieve value from parameter store
    return SSM.get_parameter(Name=f'/{env}/{name}',
                             WithDecryption=decrypt)['Parameter']['Value']

def set_value(name, decrypt=False, env=ENV):
    '''Returns a value from the environment or parameter store.'''
    if ENV == 'DEV':
        return os.getenv(name)
    elif env in ['STAG', 'PROD', 'ALL']: 
        return get_parameter(name, decrypt=decrypt, env=env)
    else:
        raise ValueError('Invalid environment.')
    
def set_llm_value(name, decrypt=False, env=ENV):
    '''Returns a value for the LLM API from the environment or parameter store.'''

    # get the llm provider
    provider = set_value('LLM_PROVIDER', decrypt=decrypt, env=env)

    return set_value(f'{provider}_{name}', decrypt=decrypt, env=env)



# use .env file for local development environment
if ENV == 'DEV':
    db_secrets = {
        'username': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }

""" # load database credentials from secrets manager for staging and production
if ENV == 'STAG' or ENV == 'PROD':
    db_secrets = json.loads(
        SM.get_secret_value(
            SecretId='''arn:aws:secretsmanager:us-west-2:148045048853:\
secret:rds!db-0edeaddf-aaff-4564-989e-5f3b7495a57f-bbOmc7'''
        )['SecretString']
    )
 """

## set configuration

django = {
    'secret_key': set_value('DJANGO_SECRET_KEY', decrypt=True, env='ALL'),
}

database = {
    'name': set_value('DB_NAME', decrypt=True),
    'user': db_secrets['username'],
    'password': db_secrets['password'],
    'endpoint': set_value('DB_ENDPOINT', decrypt=True),
    'port': set_value('DB_PORT', decrypt=True)
}

llm = {
    'provider': set_value('LLM_PROVIDER', env='ALL'),
    'summarization_target_word_count': int(set_value('LLM_SUMMARIZATION_TARGET_WORD_COUNT', env='ALL')),
    'api_key': set_llm_value('API_KEY', decrypt=True, env='ALL'),
    'model': set_llm_value('MODEL', env='ALL'),
}

file_save = {
    'path': set_value('FILE_SAVE_PATH', env='ALL'),
    'max_size': int(set_value('MAX_FILE_SIZE', env='ALL')),
    'game_setup_path': set_value('GAME_SETUP_PATH', env='ALL'),
}

s3 = {
    'bucket': set_value('S3_BUCKET'),
}

# lists of themes, timeframes, and details for if the user wants a random setup
random_setup = {
    'themes': [item.strip() for item in load_txt_file(os.path.join(file_save['game_setup_path'], 'themes.txt')).split('\n') if item],
    'timeframes': [item.strip() for item in load_txt_file(os.path.join(file_save['game_setup_path'], 'timeframes.txt')).split('\n') if item],
    'details': [item.strip() for item in load_txt_file(os.path.join(file_save['game_setup_path'], 'details.txt')).split('\n') if item]
}

# get the current version
with open('current_version.json') as f:
    current_version = json.load(f)['version']

game_version = current_version