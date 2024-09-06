''' Contains functions for initializing a game. '''

from games.models import Game, Location, Character, Skill

from prompting import prompt
from utils import add_info_to_initialization_prompt

def create_scenario_title(theme=None, timeframe=None, details=None):
    ''' 
    The first call to the LLM API, to create the title of the game scenario. 
    '''

    # create the prompt, using the theme and details
    title_prompt = add_info_to_initialization_prompt(theme, timeframe, details)

    title_prompt += 'Now generate the title of the scenario.'
    
    # prompt the LLM
    title = prompt(title_prompt, max_tokens=50, context='create_scenario_title')

    # return the title
    return title

def create_crash(title=None, theme=None, timeframe=None, details=None):
    ''' 
    Prompts an LLM for the description of the crash - the first thing the player will read - given a theme and details. 
    '''

    crash_prompt = f"The title of this scenario is {title}. Don't include the title in your response, please. " if title else 'There is no specified title. '

    # add the theme and details to the prompt
    crash_prompt = add_info_to_initialization_prompt(theme, timeframe, details, prompt=crash_prompt)

    crash_prompt += 'Now generate the opening crash scene for the game.'
    
    # return the prompt function as a generator, for streaming
    return prompt(crash_prompt, max_tokens=800, 
                    stream=True, context='create_crash')



def create_location(crash_story, title=None, theme=None, timeframe=None, details=None):
    '''
    Creates the starting location for the game.
    '''

    # add the title, theme, details, timeframe to the prompt
    location_prompt = f"The title of this scenario is {title}. " if title else 'There is no specified title. '
    location_prompt = add_info_to_initialization_prompt(theme, timeframe, details, prompt=location_prompt)

    # add the crash story
    location_prompt += f'''The characters have just crashed, and here is the crash story: {crash_story}. 
    Now generate the starting location for the game - we don't need any intro, or filler. Just the description of the location.'''

    
    # prompt the LLM for the location description
    location_description = prompt(location_prompt, max_tokens=300, context='create_location')

    # get a name for the location
    location_name_prompt = f'''
    Come up with a short, intriguing name for a location, based off the following description: {location_description}. 
    Remember - this name should be very short - only a few words. 
    Something like 'The Red Forest' or 'The Crystal Caves'. Don't say anything else other than the name.'''

    location_name = prompt(location_name_prompt, max_tokens=20)

    return location_name, location_description

def create_skills(crash_story, location_description, 
                  title=None, theme=None, timeframe=None, details=None):
    '''
    Creates the skills for the game, based off the location description and other game info.
    '''

    # add the title, theme, details, timeframe to the prompt
    skills_prompt = f"The title of this scenario is {title}. " if title else 'There is no specified title. '
    skills_prompt = add_info_to_initialization_prompt(theme, timeframe, details, prompt=skills_prompt)

    # add the crash story and location
    skills_prompt += f'''The characters have just crashed, and here is the crash story: {crash_story}.
        The description of the starting location for the game is: {location_description}.'''
    
    skills_prompt += '''Now generate 10 skills that the characters will need to survive in this location.
    Be sure to use the format that I specified.'''

    # prompt the LLM for the skills
    skills = prompt(skills_prompt, max_tokens=500, context='create_skills')

    # separate out the skills
    skills_list = [skill.split('--') for skill in skills.split('\n')]

    return skills, skills_list

def create_characters(crash_story, location_description, skills, 
                      title=None, theme=None, timeframe=None, details=None):
    '''
    Creates the characters for the game, based off the location description, skills, and other game info.
    '''

    # add the title, theme, details, timeframe to the prompt
    characters_prompt = f"The title of this scenario is {title}. " if title else 'There is no specified title. '
    characters_prompt = add_info_to_initialization_prompt(theme, timeframe, details, prompt=characters_prompt)

    # add the crash story and location
    characters_prompt += f'''The characters have just crashed, and here is the crash story: {crash_story}.
        The description of the starting location for the game is: {location_description}.
        The skills in the game are the following: {skills}.
        '''
    
    characters_prompt += '''Now generate the 3 starting characters - be sure that these are consistent with any characters 
    named thus far. Be sure to use the format that I specified.'''

    # prompt the LLM for the characters
    characters = prompt(characters_prompt, max_tokens=500, context='create_characters')

    characters_list = [character for character in characters.split('\n')]

    final_characters = []
    
    for character in characters_list:
        if character:
            name, history, physical, personality, skills = character.split('--')
            skills = skills.split(', ')
            skill_dict = {}
            for skill in skills:
                skill_name, skill_level = skill.split('|')
                skill_dict[skill_name] = skill_level
            final_characters.append({
                'name': name,
                'history': history,
                'physical': physical,
                'personality': personality,
                'skills': skill_dict
            })

    return characters, final_characters


def create_wakeup(crash_story, location_description, skills, characters, 
                  title=None, theme=None, timeframe=None, details=None):
    '''
    Creates the wakeup scene for the game, based off the location description, skills, characters, and other game info.
    '''

    # add the title, theme, details, timeframe to the prompt
    wakeup_prompt = f"The title of this scenario is {title}. " if title else 'There is no specified title. '
    wakeup_prompt = add_info_to_initialization_prompt(theme, timeframe, details, prompt=wakeup_prompt)

    # add the crash story, location, skills, and characters
    wakeup_prompt += f'''The characters have just crashed, and here is the crash story: {crash_story}.
        The description of the starting location for the game is: {location_description}.
        The skills in the game are the following: {skills}.
        The characters in the game are the following: {characters}.
        '''
    
    wakeup_prompt += '''Now generate the wakeup scene for the game. 
    Remember that the player will read this, and it should be engaging and interesting. 
    Don't start it with a title or intro or anything - just jump right into the scene.'''

    # return the prompt function as a generator, for streaming
    return prompt(wakeup_prompt, max_tokens=1000, stream=True, context='create_wakeup')

