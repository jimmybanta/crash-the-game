''' Contains functions for initializing a game. '''

from games.models import Game, Location, Character, Skill

from prompting import prompt
from utils import add_info_to_initialization_prompt

def create_scenario_title(theme=None, details=None):
    ''' The first call to the LLM API, to create the title of the game scenario. '''

    # create the prompt, using the theme and details
    title_prompt = add_info_to_initialization_prompt(theme, details)
    
    # prompt the LLM
    title = prompt(title_prompt, max_tokens=50, context='create_scenario_title')

    # return the title
    return title

def create_crash(title=None, theme=None, details=None):
    ''' Prompts an LLM for the description of the crash - the first thing the player will read - given a theme and details. '''

    crash_prompt = f"The title of this scenario is {title}. Don't include the title in your response, please. " if title else 'There is no specified title. '

    # add the theme and details to the prompt
    crash_prompt = add_info_to_initialization_prompt(theme, details, prompt=crash_prompt)
    
    # return the prompt function as a generator, for streaming
    return prompt(crash_prompt, max_tokens=800, 
                    stream=True, context='create_crash')



def create_characters(num_characters=3):
    pass