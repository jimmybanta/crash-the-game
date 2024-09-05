
import yaml

from model_prices import models


def calculate_price(model, input_length, output_length):
    return (models[model]['input_token_price'] * input_length) + (models[model]['output_token_price'] * output_length)


def load_yaml(file):
    ''' Loads a local yaml file. '''

    with open(file) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data




def add_info_to_initialization_prompt(theme, details, prompt=''):
    ''' Adds information to an initialization prompt - for use when starting a new game. '''

    # create the prompt to generate the title
    prompt += f' The theme is {theme}. ' if theme else 'There is no specified theme. '

    # add details
    if details:
        prompt += 'The following details will be incorporated into the scenario: '
        for detail in details.split(','):
            prompt += f'{detail},'
        # remove the trailing comma
        prompt = prompt[:-1]
        # add a period
        prompt += '.'


    return prompt