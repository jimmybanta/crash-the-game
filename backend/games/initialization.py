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
    title, cost = prompt(title_prompt, max_tokens=50, context='create_scenario_title', caching=False)

    # return the title and the cost to generate it
    return title, cost

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
                    stream=True, context='create_crash', caching=False)



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
    location_description, description_cost = prompt(location_prompt, max_tokens=300, context='create_location', caching=False)

    # get a name for the location
    location_name_prompt = f'''
    Come up with a short, intriguing name for a location, based off the following description: {location_description}. 
    Remember - this name should be very short - only a few words. 
    Something like 'The Red Forest' or 'The Crystal Caves'. Don't say anything else other than the name.'''

    location_name, name_cost = prompt(location_name_prompt, max_tokens=20, caching=False)

    return location_name, location_description, description_cost + name_cost

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
    
    skills_prompt += '''Now generate 5-10 skills that the characters will need to survive in this location.
    Be sure to use the format that I specified.'''

    formatting_correct = False
    attempts = 0

    total_cost = 0

    while not formatting_correct:
        attempts += 1
        # prompt the LLM for the skills
        raw_skills, cost = prompt(skills_prompt, max_tokens=500, context='create_skills', caching=False)
        total_cost += cost

        # skills list will be a well-formatted list of the skills
        skills_list = []

        for skill in raw_skills.split('\n'):
            if skill:
                # split the skill into its parts
                # if this doesn't work, then the formatting was incorrect, 
                # or maybe it added an intro or something
                # so skip it - and at the end we'll check if we have enough skills
                # if we don't, we'll re-prompt until it gets it right
                try:
                    name, description = skill.split('--')
                    # remove any underscores or dashes
                    name = name.strip().replace('_', ' ').replace('-', ' ')
                    # capitalize the first letter of each word
                    name = ' '.join([word.capitalize() for word in name.split()])
                except:
                    continue

                skills_list.append((name, description))

        # check if the formatting is correct
        if len(skills_list) >= 5 and len(skills_list) <= 10:
            if all([len(skill) == 2 and all(skill) for skill in skills_list]):
                formatting_correct = True

        if attempts > 5:
            return 'Too many attempts. Please try again.', None
        
    # create a new skills string from the skills list
    skills_str = ''
    for skill in skills_list:
        skills_str += f'{skill[0]}--{skill[1]}\n'

    return skills_str, skills_list, total_cost

def create_characters(crash_story, location_description, skills_str,
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
        The skills in the game are the following: {skills_str}.
        '''
    
    characters_prompt += '''Now generate the 3 starting characters - be sure that these are consistent with any characters 
    named thus far. Be sure to use the format that I specified.'''

    # prompt the LLM for the characters
    formatting_correct = False

    attempts = 0
    total_cost = 0

    while not formatting_correct:
        attempts += 1
        
        raw_characters, cost = prompt(characters_prompt, max_tokens=1000, context='create_characters')
        total_cost += cost
        
        characters_list = []
        
        for character in raw_characters.split('\n'):
            if character:
                # split the character into its parts
                # if this doesn't work, then the formatting was incorrect, 
                # or maybe it added an intro or something
                # so skip it - and at the end we'll check if we have 3 characters
                # if we don't, we'll re-prompt until it gets it right
                try:
                    name, history, physical, personality, skills = character.split('--')
                except:
                    print('character problem:', character)
                    continue

                skill_dict = {}
                for skill in skills.split(','):
                    try:
                        skill_name, skill_level = skill.split('|')
                        # remove any underscores or dashes
                        skill_name = skill_name.strip().replace('_', ' ').replace('-', ' ')
                        # capitalize the first letter of each word
                        skill_name = ' '.join([word.capitalize() for word in skill_name.split()])
                    except:
                        print('skill problem:', skill)
                        continue
                    skill_dict[skill_name] = skill_level

                characters_list.append({
                    'name': name,
                    'history': history,
                    'physical': physical,
                    'personality': personality,
                    'skills': skill_dict
                })

        # check if the formatting is correct
        if len(characters_list) == 3:
            formatting_correct = True
        else:
            print('Characters list:', characters_list)
            print('Characters:', raw_characters)
            input()
        
        if attempts > 5:
            return 'Too many attempts. Please try again.', None
        
    # create a new characters string from the characters list
    characters_str = ''
    for character in characters_list:
        skills_str = ', '.join([f'{skill}|{level}' for skill, level in character['skills'].items()])
        characters_str += f"{character['name']}--{character['history']}--{character['physical']}--{character['personality']}--{skills_str}\n"
    
    print(characters_str)
    print(characters_list)
    print(total_cost)

    return characters_str, characters_list, total_cost


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
    return prompt(wakeup_prompt, max_tokens=1000, stream=True, context='create_wakeup', caching=False)

