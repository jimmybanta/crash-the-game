''' The views for the server. '''

import json
import logging
import os
import time
import requests
from uuid import uuid4

from django_eventstream import send_event
from django.core.mail import send_mail
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework import viewsets

import config

import games.initialization as initialization
from games.load_game import load_history, load_latest_file, load_json
from games.models import Game, Location, Character, Skill
from games.prompting import prompt
from games.save_game import save_text, remove_turn
from games.serializers import CharacterSerializer, SkillSerializer
from games.summarize import summarize, fix_summary_history


logger = logging.getLogger(__name__)


## Viewsets

# use a custom exception for API errors
# this will allow frontend to handle it
class CustomAPIException(APIException):
    status_code = 255
    default_detail = 'Problem retrieving objects.'
    default_code = 'custom_error'

class CharacterViewSet(viewsets.ModelViewSet):
    '''
    API endpoint that allows characters to be viewed.

    Parameters
    ----------
    game_id : int
        The ID of the game that the characters are in.
    '''
    serializer_class = CharacterSerializer

    def get_queryset(self):
        game_id = self.request.query_params.get('game_id', None)
        if game_id is not None:

            try:
                game = Game.objects.get(id=game_id)
                # get all characters for the current game
                characters = game.characters.all()
                return characters.order_by('id')
            except:
                raise CustomAPIException()
        
        else:
            raise CustomAPIException()
        
class SkillViewSet(viewsets.ModelViewSet):
    '''
    API endpoint that allows skills to be viewed.

    Parameters
    ----------
    game_id : int
        The ID of the game that the skills are in.
    '''
    serializer_class = SkillSerializer

    def get_queryset(self):
        game_id = self.request.query_params.get('game_id', None)
        if game_id is not None:

            try:
                game = Game.objects.get(id=game_id)
                # get all skills for the current game
                skills = game.skills.all()
                return skills.order_by('id')
            except:
                raise CustomAPIException()
        
        else:
            raise CustomAPIException()


## API Views

@csrf_exempt
@api_view(['GET'])
def get_current_version(request):
    '''
    Returns the current version of the game.
    '''

    return JsonResponse({'version': config.game_version})

@csrf_exempt
@api_view(['POST'])
def initialize_save_key(request):
    '''
    Creates a game, and a unique UUID for it, then returns the key for the user to have. 
    '''

    # generate a new key
    save_key = uuid4()

    try:
        # create the game with the key
        game = Game.objects.create(
            save_key=save_key
        )
    except:
        warning = 'Error creating game.'
        logger.exception(warning)
        return HttpResponse(f'{warning} Please try again.', status=255)

    logger.info(f'Game created with id={game.id} and save key={save_key}')

    # return the key and game ID, so the frontend can keep track of the game
    return JsonResponse({'save_key': save_key, 'game_id': game.id })

@csrf_exempt
@api_view(['GET'])
def random_setup(request):
    '''
    Returns a random setup for a game.
    '''

    theme, timeframe, details = initialization.random_setup()

    return JsonResponse({
        'theme': theme,
        'timeframe': timeframe,
        'details': details
    })

@csrf_exempt
@api_view(['POST'])
def initialize_game_title(request):
    '''
    Given a theme and details, creates a title for the game scenario and returns it to the frontend.

    API Parameters
    --------------
    game_id : int
        The ID of the game.
    theme : str
        The theme of the game.
    timeframe : str
        The timeframe of the game.
    details : str
        The details of the game.
    '''

    
    # get parameters
    game_id = request.data['game_id']
    theme = request.data['theme']
    timeframe = request.data['timeframe']
    details = request.data['details']

    try:
        # generate the title and the cost to create it
        title, cost = initialization.create_title(theme=theme, timeframe=timeframe, details=details)

        # update the game
        game = Game.objects.get(id=game_id)
        game.theme = theme
        game.timeframe = timeframe
        game.starting_details = details
        game.title = title
        game.total_dollar_cost += cost
        game.save()
    except:
        logger.exception(f'Error initializing game title.')
        return HttpResponse('Error initializing game. Please try again.', status=255)
    
    logger.info(f'Game title created for game id={game_id}: {title} -- theme: {theme}, timeframe: {timeframe}, details: {details}')

    # send me an email with game info
    try:
        # get the user's IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # get the location
        response = requests.get(f'http://ip-api.com/json/{ip}')

        country = response.json()['country']
        region = response.json()['regionName']
        city = response.json()['city']
    except:
        message = f'''Error getting user location.
        x_forwarded_for = {x_forwarded_for}
        ip = {ip}
        response = {response}
        '''
        logger.exception(message)
        country = 'Unknown'
        region = 'Unknown'
        city = 'Unknown'
        
    try:
        # send myself an email with the game info
        send_mail(
            title,
            f'''New game of Crash:

        Game ID: {game_id}

        Theme: {theme}
        Timeframe: {timeframe}
        Details: {details}

        User location: {city}, {region}, {country}
        Current env: {config.ENV}
            ''',
            config.email['from_address'],
            [config.email['to_address']],
        )
    # if there's an error, log it and move on
    except:
        logger.exception('Error sending email with game info.')
        pass

    # return the title
    return JsonResponse({'title': title})

@csrf_exempt
@api_view(['POST'])
def initialize_game_crash(request):
    '''
    Given a game (which should now have a theme, details, and a title), 
    generates a crash story, to be sent back to the frontend.

    API Parameters
    --------------
    game_id : int
        The ID of the game.
    '''

    # wait some time, to let the player read the title
    time.sleep(1)
    
    # get parameters
    game_id = request.data['game_id']

    # get the game
    game = Game.objects.get(id=game_id)

    logger.info(f'Generating crash story for game id={game_id}')

    crash_story = ''

    try:
        # iterate through
        for chunk in initialization.create_crash(title=game.title, theme=game.theme,
                                        timeframe=game.timeframe, details=game.starting_details):
            
            if chunk['type'] == 'text':
                crash_story += chunk['text']
                send_event(f'game-{game.id}', 'message', {'text': chunk['text']})
            elif chunk['type'] == 'message_stop':
                cost = chunk['cost']
                game.total_dollar_cost += cost
    except:
        logger.exception(f'Error generating crash story for game id={game_id}')
        return HttpResponse('There was a problem initializing the game. Please try again.', status=255)

    try:
        # save the crash story to file
        save_text(game_id=game_id, new_data=crash_story, turn='crash', writer='ai')

        # summarize the crash story
        summary, summary_cost = summarize(crash_story, target_words=config.llm['summarization_target_word_count'])

        # save a user message to summary file
        crash_message = 'Start the story for me - have them crash land.'
        save_text(game_id=game_id, new_data=crash_message, writer='user', turn='crash', type='summaries')

        # then save the summary to file
        save_text(game_id=game_id, new_data=summary, writer='ai', turn='crash', type='summaries')

        # update the game cost
        game.total_dollar_cost += summary_cost
        game.save()
    except:
        logger.exception(f'Error summarizing and saving crash story for game id={game_id}')
        return HttpResponse('There was a problem initializing the game. Please try again.', status=255)
    
    logger.info(f'Crash story generated for game id={game_id}')

    # return the crash story so it can get passed to the next step
    return JsonResponse({'crash_story': crash_story})

@csrf_exempt
@api_view(['POST'])
def initialize_game_wakeup(request):
    '''
    Given a game, generates the wake-up scene for the player.

    API Parameters
    --------------
    game_id : int
        The ID of the game.
    crash_story : str
        The crash story of the game.
    '''
    
    # get parameters
    game_id = request.data['game_id']
    crash_story = request.data['crash_story']

    try:
        # get the game
        game = Game.objects.get(id=game_id)

        # first, we need to generate the starting location description
        location_name, location_description, location_cost = initialization.create_location(crash_story, title=game.title, theme=game.theme,
                                                                                            timeframe=game.timeframe, details=game.starting_details)

        # then, create a new location object
        location = Location.objects.create(
            name=location_name,
            description=location_description
        )

        # add the location to the game
        game.locations.add(location)
        # update game cost
        game.total_dollar_cost += location_cost
        game.save()

        # save location info to the initialization file
        save_text(game_id=game_id, new_data=f'Location name: {location_name}', writer='ai', type='initialization')
        save_text(game_id=game_id, new_data=f'Location description: {location_description}', writer='ai', type='initialization')

        # now we need to generate skills that match the location/scenario
        skills_str, skills_list, skills_cost = initialization.create_skills(crash_story, location_description, 
                                                                            title=game.title, theme=game.theme,
                                                                            timeframe=game.timeframe, details=game.starting_details)
    
        # create skill objects and add to the game
        for name, description in skills_list:
            skill = Skill.objects.create(
                name=name,
                description=description
            )

            game.skills.add(skill)
        
        # update game cost
        game.total_dollar_cost += skills_cost
        game.save()

        # save skills to file
        save_text(game_id=game_id, new_data=f'Skills: {skills_str}', writer='ai', type='initialization')
    


        # now, we need to generate characters that match the location, scenario, and skills
        characters_str, characters_list, characters_cost = initialization.create_characters(crash_story, location_description, skills_str,
                                                                                            title=game.title, theme=game.theme,
                                                                                            timeframe=game.timeframe, details=game.starting_details)
    
        # create the character objects and add to the game
        # characters list is a list of character dicts
        for character in characters_list:
                
            new_character = Character.objects.create(
                name=character['name'],
                history=character['history'],
                physical_description=character['physical'],
                personality=character['personality'],
                skills=character['skills']
            )

            game.characters.add(new_character)

        # update game cost
        game.total_dollar_cost += characters_cost
        game.save()

        # save characters to file
        save_text(game_id=game_id, new_data=f'Characters: {characters_str}', writer='ai', type='initialization')
    
    except:
        logger.exception(f'Error generating wakeup info for game id={game_id}')
        return HttpResponse('There was a problem initializing the game. Please try again.', status=255)

    logger.info(f'Generating wakeup scene for game id={game_id}')

    # finally, create the wake up scene, and return it to the player
    wakeup_story = ''

    # iterate through the wakeup story
    try:
        for chunk in initialization.create_wakeup(crash_story, location_description, skills_str, characters_str,
                                                    title=game.title, theme=game.theme,
                                                    timeframe=game.timeframe, details=game.starting_details):
            
            # if it's text, yield it
            if chunk['type'] == 'text':
                wakeup_story += chunk['text']
                send_event(f'game-{game.id}', 'message', {'text': chunk['text']})
            # the last chunk will be the message stop, which has cost data
            elif chunk['type'] == 'message_stop':
                # add the cost to generate it
                cost = chunk['cost']
                game.total_dollar_cost += cost
    except:
        logger.exception(f'Error generating wakeup story for game id={game_id}')
        return HttpResponse('There was a problem initializing the game. Please try again.', status=255)
    
    try:
        # save wakeup story to file
        save_text(game_id=game_id, new_data=wakeup_story, turn='wakeup', writer='ai')

        # summarize the wakeup story
        summary, summary_cost = summarize(wakeup_story, target_words=config.llm['summarization_target_word_count'])

        # save a user message to summary file
        wakeup_message = 'Now tell the story of them waking up in this new, strange place.'
        save_text(game_id=game_id, new_data=wakeup_message, writer='user', turn='wakeup', type='summaries')

        # then save the summary to file
        save_text(game_id=game_id, new_data=summary, writer='ai', turn='wakeup', type='summaries')

        # update game cost
        game.total_dollar_cost += summary_cost
        game.save()
    except:
        logger.exception(f'Error summarizing and saving wakeup story for game id={game_id}')
        return HttpResponse('There was a problem initializing the game. Please try again.', status=255)

    # return success
    return JsonResponse({'success': "we're looking good back here frontend - thanks for all your hard work"})

@csrf_exempt
@api_view(['POST'])
def initialize_game_intro(request):
    '''
    Returns the game intro to the player.

    API Parameters
    --------------
    game_id : int
        The ID of the game.
    '''

    # get the game ID
    game_id = request.data['game_id']

    ## if we have trouble with these things, don't abort the game
    ## just don't include the character names in the intro
    # get the game
    try:
        game = Game.objects.get(id=game_id)
    except:
        logger.exception(f'Error getting game id={game_id}')
        character_names = None

    # get the game character names
    try:
        character_names = [character.name.split()[0] for character in game.characters.all()]
    except:
        logger.exception(f'Error getting character names for game id={game_id}')
        character_names = None

    if not character_names:
        starting_str = 'Some poor souls'
    else:
        starting_str = f'{character_names[0]}, {character_names[1]}, and {character_names[2]}'

        
    # get the game intro
    intro = f'''{starting_str} need your help!
They're lost in a strange world, the unwitting and unwilling heroes of a story that they didn't want to be a part of.
Now you - that's right, YOU - need to guide them through that story.

Think of yourself as an angel (or devil), sitting on their shoulders, whispering in their ears.
Each turn, you'll make suggestions and interact with your characters.

Speaking of the characters - on the right -> of the screen, you can see more info about your characters - their histories, personalities, skills.
Be creative, be bold, be kind, be cruel. Do whatever you like - the world is your oyster!

Speaking of the right of the screen - in the bottom right you should see a button that says 'Save Key'. 
Click it.

So - what will you do next?'''
    
    # save the intro to file
    ## if we can't, skip it
    ## this will only affect if the player loads the game at a future time,
    ## and they won't see the intro
    try:
        save_text(game_id=game_id, new_data=intro, writer='intro', turn='intro')
    except:
        logger.exception(f'Error saving intro for game id={game_id}')
        pass

    logger.info(f'Streaming game intro for game id={game_id}')
    
    # stream back the response
    # if we have problems streaming it back, then raise an error
    try:
        for chunk in intro:
            time.sleep(0.007)
            send_event(f'game-{game_id}', 'message', {'text': chunk})
    except:
        logger.exception(f'Error streaming intro for game id={game_id}')
        return HttpResponse('There was a problem initializing the game. Please try again.', status=255)

    return JsonResponse({'success': 'we are good to go - do your thing frontend'})

@csrf_exempt
@api_view(['POST'])
def load_game_info(request):
    '''
    Loads the game info - title, theme, timeframe, and details - for the player.

    API Parameters
    --------------
    save_key : str
        The save key for the game.
    '''

    # get the save key
    save_key = request.data['save_key']

    try:
        game = Game.objects.get(save_key=save_key)
    except:
        warning = 'Invalid save key.'
        logger.exception(warning)
        return HttpResponse(warning, status=255)
    
    logger.info(f'Loading game info for game id={game.id}')

    # get the game info and return it
    game_info = {
        'id': game.id,
        'title': game.title,
        'theme': game.theme,
        'timeframe': game.timeframe,
        'details': game.starting_details,
        'turns': game.turns,
    }
    return JsonResponse(game_info)

@csrf_exempt
@api_view(['POST'])
def load_game(request):
    '''
    Loads a game from a save key.
    '''

    # wait a couple seconds so the player can read the title, it doesn't all get thrown at once
    time.sleep(1)

    save_key = request.data['save_key']

    try:
        game = Game.objects.get(save_key=save_key)
    except:
        logger.exception(f'Problem finding game with save key {save_key}')
        return HttpResponse('There was a problem retrieving your game - please try again.', status=255)

    # load the game history
    history = load_history(game.id)

    logger.info(f'Loading game for game id={game.id}')

    # stream back the response
    # want it to take a max of 4 seconds
    time_per_chunk = 4 / len(history)
    try:
        for item in history:
            time.sleep(min(time_per_chunk, 0.3))
            send_event(f'game-{game.id}', 'message', {'item': item})
    except:
        logger.exception(f'Error streaming game for game id={game.id}')
        return HttpResponse('There was a problem retrieving your game - please try again.', status=255)
    
    return JsonResponse({'success': 'game loaded - have fun!'})

@csrf_exempt
@api_view(['POST'])
def main_loop(request):
    '''
    The main loop of the game.

    API Parameters
    --------------
    game_id : int
        The ID of the game.
    user_input : str
        The user input.
    history : list
        The history of the game.
    turn : int
        The current turn.
    '''

    game_id = request.data['game_id']
    user_input = request.data['user_input']
    turn = int(request.data['turn'])

    # frontend history - all the text displayed in the frontend
    ## includes the crash story, wakeup story, game intro, then all user input and AI responses
    ## ends in the current user input
    frontend_history = request.data['history']
    
    # first, check to see if the last item in summaries/full text is a user message
    ## if it is, then remove it
    ## something probably went wrong, preventing the AI from responding to it
    try:
        full_text = load_latest_file(game_id, type='full_text')
        summaries = load_latest_file(game_id, type='summaries')

        if full_text[-1]['writer'] == 'user':
            logger.info('Removing user message from full text.')
            full_text = full_text[:-1]
            save_text(game_id=game_id, new_data=full_text, writer='ai', save_type='overwrite')
        
        if summaries[-1]['writer'] == 'user':
            logger.info('Removing user message from summaries.')
            summaries = summaries[:-1]
            save_text(game_id=game_id, new_data=summaries, writer='ai', save_type='overwrite', type='summaries')
    # if something goes wrong log it and pass
    except:
        logger.exception('Problem checking for user message in summaries/full text.')
        pass

    
    # create the system prompt and history
    try:
        ## first, add the theme, timeframe, and details to the system prompt
        game = Game.objects.get(id=game_id)
    
        main_loop_prompt = 'Here is the title, theme, timeframe, and details of the game:\n'

        main_loop_prompt += f'Title: {game.title}\n' if game.title else 'There is no specified title.\n'
        main_loop_prompt += f'Theme: {game.theme}\n' if game.theme else 'There is no specified theme.\n'
        main_loop_prompt += f'Timeframe: {game.timeframe}\n' if game.timeframe else 'There is no specified timeframe.\n'
        main_loop_prompt += f'Details: {game.starting_details}\n\n' if game.starting_details else 'There are no specified details.\n\n'

        ## then, add the location, skills, and characters to the system prompt

        game_initialization_path = os.path.join(config.file_save['path'], str(game_id), 'initialization.json')

        data = load_json(game_initialization_path)

        location_name = data[0]['text']
        location_description = data[1]['text']
        skills = data[2]['text']
        characters = data[3]['text']

        main_loop_prompt += 'Here are the location name, description, skills, and characters:\n'
        main_loop_prompt += f'{location_name}\n'
        main_loop_prompt += f'{location_description}\n'
        main_loop_prompt += 'But remember - they may not be in this location anymore. This is just the location where the story started.\n'
        main_loop_prompt += f'{skills}\n'
        main_loop_prompt += f'{characters}\n\n'

        main_loop_prompt += '''Here is the history of the game thus far:
Each of these, except for the last, is a summary of what happened.
The last is the full text. What you output should be more like the full text.\n\n'''

        ## now, add the history
        history = load_history(game_id, summaries=True)
        
        # remove the last AI message
        if history[-1]['writer'] == 'ai':
            history = history[:-1]

        # replace it with the last full text AI response
        for item in frontend_history[::-1]:
            if item['writer'] == 'ai':
                item['text'] = item['text'].strip()
                history.append(item)
                break
        
        # then, add the user input and some gentle encouragement and tips
        ## have to tell it not to create monsters, or else that's ALL it does
        history.append({'writer': 'user', 
                        'text': f'''{user_input}. Remember to keep it around 150-250 words.
When in doubt, make something surprising and exciting happen!
Avoid creating monsters and scary creatures - we're looking for drama, funny characters, and bizarre twists!'''})
        
        # check the history, and fix it if necessary
        history_fixed = fix_summary_history(history)
    except:
        logger.exception(f'Problem generating main loop prompt and history for game id={game_id}')
        return HttpResponse('There was a problem - please try again.', status=255)
    
    logger.info(f'Generating main loop response for game id={game_id}')

    response = ''
    try:
        for chunk in prompt(history_fixed, context='main_loop', 
                            system=main_loop_prompt, stream=True, caching=True):
        
            if chunk['type'] == 'text':
                response += chunk['text']
                send_event(f'game-{game_id}', 'message', {'text': chunk['text']})
            elif chunk['type'] == 'message_stop':
                # add the cost to generate it
                cost = chunk['cost']
                game.total_dollar_cost += cost
    except:
        logger.exception(f'Error generating main loop response for game id={game_id}')
        return HttpResponse('There was a problem - please try again.', status=255)
    

    try:
        # summarize the response
        summary, summary_cost = summarize(response, target_words=config.llm['summarization_target_word_count'])

        # update game
        game.turns = turn
        game.total_dollar_cost += summary_cost
        game.save()

        ## saving text

        # first, save the user input to both the full text and summary files
        save_text(game_id=game_id, new_data=user_input, writer='user', turn=turn, type='full_text')
        save_text(game_id=game_id, new_data=user_input, writer='user', turn=turn, type='summaries')

        # then save the response to file
        save_text(game_id=game_id, new_data=response, turn=turn, writer='ai', type='full_text')

        # then save the summmary to file
        save_text(game_id=game_id, new_data=summary, turn=turn, writer='ai', type='summaries')

    except:
        # something has gone wrong, so we need to reset the turn

        # remove the turn from the summary and full text files
        remove_turn(game_id, turn)

        game.turns = turn - 1
        # save the game
        game.save()

        logger.exception(f'Error summarizing and saving main loop response for game id={game_id}')
        
        return HttpResponse('There was a problem - please try again.', status=255)

    return JsonResponse({'success': 'locked and loaded - knock their socks off!'})


    




