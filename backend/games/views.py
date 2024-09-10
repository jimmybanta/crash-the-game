from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from rest_framework import viewsets

import time
from uuid import uuid4
import json

import config

from games.serializers import CharacterSerializer, SkillSerializer

from games.models import Game, Location, Character, Skill

from games.initialization import create_scenario_title, create_crash, create_location, create_skills, create_characters, create_wakeup
from games.summarize import summarize, fix_summary_history
from games.save_game import save_text
from games.load_game import load_history, load_history_summary, load_latest_file

from prompting import prompt


DEV_GAME_ID = 162

# Create your views here.

## Viewsets

class CharacterViewSet(viewsets.ModelViewSet):
    '''
    API endpoint that allows characters to be viewed.
    '''
    serializer_class = CharacterSerializer

    def get_queryset(self):
        game_id = self.request.query_params.get('game_id', None)
        if game_id is not None:

            game = Game.objects.get(id=game_id)
            # get all characters for the current game
            characters = game.characters.all()
            return characters.order_by('id')
        
        else:
            return None
        
class SkillViewSet(viewsets.ModelViewSet):
    '''
    API endpoint that allows skills to be viewed.
    '''
    serializer_class = SkillSerializer

    def get_queryset(self):
        game_id = self.request.query_params.get('game_id', None)
        if game_id is not None:

            game = Game.objects.get(id=game_id)
            # get all skills for the current game
            skills = game.skills.all()
            return skills.order_by('id')
        
        else:
            return None

@csrf_exempt
@api_view(['GET'])
def get_current_version(request):
    '''
    Returns the version of the game.
    '''

    return JsonResponse({'version': config.game_version['version']})


@csrf_exempt
@api_view(['POST'])
def check_save_key(request):
    '''
    Checks if a save key is valid.
    '''

    save_key = request.data['save_key']

    try:
        _ = Game.objects.get(save_key=save_key)
        return JsonResponse({'valid': True})
    except:
        return JsonResponse({'valid': False})



@csrf_exempt
@api_view(['POST'])
def initialize_game_key(request):
    '''
    Creates a game, and a unique UUID for it, then returns the key for the user to have. 
    '''

    dev = request.data['dev']
    if dev == 'true':
        time.sleep(1)

        game = Game.objects.get(id=DEV_GAME_ID)
        return JsonResponse({
            'save_key': game.save_key, 
            'game_id': DEV_GAME_ID})

    # generate a new key
    save_key = uuid4()

    # create the game with the key
    game = Game.objects.create(
        save_key=save_key
    )

    # return the key and game ID, so the frontend can keep track of the game
    return JsonResponse({'save_key': save_key, 'game_id': game.id })




@csrf_exempt
@api_view(['POST'])
def initialize_game_title(request):
    '''
    Given a theme and details, creates a title for the game scenario and returns it to the frontend.
    '''
    
    game_id = request.data['game_id']
    theme = request.data['theme']
    timeframe = request.data['timeframe']
    details = request.data['details']

    dev = request.data['dev']
    if dev == 'true':
        time.sleep(1)
        game = Game.objects.get(id=DEV_GAME_ID)
        return JsonResponse({'title': game.title})

    # generate the title
    title = create_scenario_title(theme=theme, timeframe=timeframe, details=details)

    # update the game with this info
    game = Game.objects.get(id=game_id)
    game.theme = theme
    game.timeframe = timeframe
    game.starting_details = details
    game.title = title
    game.save()

    return JsonResponse({'title': title})


@csrf_exempt
@api_view(['POST'])
def initialize_game_crash(request):
    '''
    Given a game (which should now have a theme, details, and a title), 
    generates a crash scenario, to be sent back to the frontend.
    '''

    # wait a couple seconds, to let the player read the title
    time.sleep(0.5)
    
    game_id = request.data['game_id']


    dev = request.data['dev']
    if dev == 'true':
        time.sleep(0.5)
        with open(f'/Users/jimbo/Documents/coding/projects/survival-game/backend/game_files/{DEV_GAME_ID}/full_text/0.json', 'r') as f:
            data = json.load(f)

            def generate_response():
                for char in data[0]['text']:
                    time.sleep(0.0001)
                    yield char

            return StreamingHttpResponse(generate_response(), content_type='text/plain')

    # get the game
    game = Game.objects.get(id=game_id)

    # create a custom generator
    def generate_response():
        crash_story = ''

        # iterate through the crash story
        for chunk in create_crash(title=game.title, theme=game.theme,
                                timeframe=game.timeframe, details=game.starting_details):
            crash_story += chunk
            yield chunk
        
        # save the crash story to file
        save_text(game_id=game_id, text=crash_story, writer='ai')

        # summarize the crash story
        summary = summarize(crash_story, target_words=config.llm['summarization_target_word_count'])

        # save a human message to summary file
        crash_message = 'Start the story for me - have them crash land.'
        save_text(game_id=game_id, text=crash_message, writer='human', type='summaries')

        # save the summary to file
        save_text(game_id=game_id, text=summary, writer='ai', type='summaries')



    # generate the crash and return it as a streaming response
    response = StreamingHttpResponse(generate_response(), content_type='text/plain')

    return response



@csrf_exempt
@api_view(['POST'])
def initialize_game_wakeup(request):
    '''
    Given a game, generates the wake-up scene for the player.
    '''
    
    game_id = request.data['game_id']
    crash_story = request.data['crash_story']

    dev = request.data['dev']
    if dev == 'true':
        def generate_response():
            with open(f'/Users/jimbo/Documents/coding/projects/survival-game/backend/game_files/{DEV_GAME_ID}/full_text/0.json', 'r') as f:
                data = json.load(f)

                for char in data[1]['text']:
                    time.sleep(0.0001)
                    yield char
        return StreamingHttpResponse(generate_response(), content_type='text/plain')


    game = Game.objects.get(id=game_id)

    # first, we need to generate the starting location description
    location_name, location_description = create_location(crash_story, title=game.title, theme=game.theme,
                                        timeframe=game.timeframe, details=game.starting_details)
    
    # then, create a new location object
    location = Location.objects.create(
        name=location_name,
        description=location_description
    )

    # add the location to the game
    game.locations.add(location)

    game.save()

    # save location info to file
    save_text(game_id=game_id, text=f'Location name: {location_name}', writer='ai', type='initialization')
    save_text(game_id=game_id, text=f'Location description: {location_description}', writer='ai', type='initialization')

    # now we need to generate skills that match the location/scenario
    skills, skills_list = create_skills(crash_story, location_description, 
                            title=game.title, theme=game.theme,
                            timeframe=game.timeframe, details=game.starting_details)
        
    for name, description in skills_list:
        skill = Skill.objects.create(
            name=name,
            description=description
        )

        game.skills.add(skill)

    game.save()

    # save skills to file
    save_text(game_id=game_id, text=f'Skills: {skills}', writer='ai', type='initialization')

    # now, we need to generate characters that match the location, scenario, and skills
    characters, characters_list = create_characters(crash_story, location_description, skills,
                                                title=game.title, theme=game.theme,
                                                timeframe=game.timeframe, details=game.starting_details)
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

    game.save()

    # save characters to file
    save_text(game_id=game_id, text=f'Characters: {characters}', writer='ai', type='initialization')

    # finally, create the wake up scene, and return it to the player

    # create a custom generator
    def generate_response():
        wakeup_story = ''

        # iterate through the wakeup story
        for chunk in create_wakeup(crash_story, location_description, skills, characters,
                                title=game.title, theme=game.theme,
                                timeframe=game.timeframe, details=game.starting_details):
            wakeup_story += chunk
            yield chunk
        
        # save the wakeup story to file
        save_text(game_id=game_id, text=wakeup_story, writer='ai')

        # summarize the wakeup story
        summary = summarize(wakeup_story, target_words=config.llm['summarization_target_word_count'])

        # save a human message to summary file
        wakeup_message = 'Now tell the story of them waking up in this new, strange place.'
        save_text(game_id=game_id, text=wakeup_message, writer='human', type='summaries')

        # then save the summary to file
        save_text(game_id=game_id, text=summary, writer='ai', type='summaries')


    # generate the crash and return it as a streaming response
    response = StreamingHttpResponse(generate_response(), content_type='text/plain')

    return response


@csrf_exempt
@api_view(['POST'])
def initialize_game_intro(request):
    '''
    Returns the game intro to the player.
    '''

    game_id = request.data['game_id']

    game = Game.objects.get(id=game_id)

    # get the game characters
    characters = game.characters.all()

    # get their names
    character_names = [character.name.split()[0] for character in characters]

    # get the game intro
    intro = f'''{character_names[0]}, {character_names[1]}, and {character_names[2]} need your help!
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
    save_text(game_id=game_id, text=intro, writer='intro')
    
    # stream back the response
    def generate_response():
        for chunk in intro:
            time.sleep(0.01)
            yield chunk


    return StreamingHttpResponse(generate_response(), content_type='text/plain')


@csrf_exempt
@api_view(['POST'])
def load_game_info(request):
    '''
    Loads the game info - title, theme, timeframe, and details - for the player.
    '''

    save_key = request.data['save_key']

    try:
        game = Game.objects.get(save_key=save_key)
    except:
        return JsonResponse({'error': 'Invalid save key.'})

    # get the game info
    game_info = {
        'id': game.id,
        'title': game.title,
        'theme': game.theme,
        'timeframe': game.timeframe,
        'details': game.starting_details
    }

    return JsonResponse(game_info)


@csrf_exempt
@api_view(['POST'])
def load_game(request):
    '''
    Loads a game from a save key.
    '''

    time.sleep(2)

    save_key = request.data['save_key']

    game = Game.objects.get(save_key=save_key)

    # load the game history
    history = load_history(game.id)

    def generate_response():
        for item in history:
            time.sleep(0.3)
            yield json.dumps(item)

    return StreamingHttpResponse(generate_response(), content_type='application/json')
        

@csrf_exempt
@api_view(['POST'])
def main_loop(request):
    '''
    The main loop of the game.
    '''

    game_id = request.data['game_id']
    user_input = request.data['user_input']
    # frontend history - all the text displayed in the frontend
    ## includes the crash story, wakeup story, game intro, then all user input and AI responses
    ## ends in the current user input
    frontend_history = request.data['history']

    # first, check to see if the last item in summaries/full text is a user message
    ## if it is, then remove it
    ## something probably went wrong, preventing the AI from responding to it
    full_text = load_latest_file(game_id, type='full_text')
    summaries = load_latest_file(game_id, type='summaries')

    if full_text[-1]['writer'] == 'human':
        print('removing last human message')
        full_text = full_text[:-1]
        save_text(game_id=game_id, text=full_text, writer='ai', save_type='overwrite')
    
    if summaries[-1]['writer'] == 'human':
        print('removing last human message')
        summaries = summaries[:-1]
        save_text(game_id=game_id, text=summaries, writer='ai', save_type='overwrite', type='summaries')


    # then, save the user input to both the full text and summary files
    save_text(game_id=game_id, text=user_input, writer='human', type='full_text')
    save_text(game_id=game_id, text=user_input, writer='human', type='summaries')

    try:
        dev = request.data['dev']
    except:
        dev = 'false'
    if dev == 'true':
        time.sleep(1)
        with open(f'/Users/jimbo/Documents/coding/projects/survival-game/backend/game_files/{DEV_GAME_ID}/full_text/0.json', 'r') as f:
            data = json.load(f)

            save_text(game_id=game_id, text=data[4]['text'], writer='ai')

            def generate_response():
                for char in data[4]['text']:
                    time.sleep(0.001)
                    yield char

            return StreamingHttpResponse(generate_response(), content_type='text/plain')

    ## first, add the theme, timeframe, and details to the system prompt
    game = Game.objects.get(id=game_id)
    
    main_loop_prompt = 'Here is the title, theme, timeframe, and details of the game:\n'

    main_loop_prompt += f'Title: {game.title}\n' if game.title else 'There is no specified title.\n'
    main_loop_prompt += f'Theme: {game.theme}\n' if game.theme else 'There is no specified theme.\n'
    main_loop_prompt += f'Timeframe: {game.timeframe}\n' if game.timeframe else 'There is no specified timeframe.\n'
    main_loop_prompt += f'Details: {game.starting_details}\n\n' if game.starting_details else 'There are no specified details.\n\n'

    ## then, add the location, skills, and characters to the system prompt
    game_initialization_path = f'{config.file_save["path"]}/{game_id}/initialization/0.json'

    with open(game_initialization_path, 'r') as f:
        data = json.load(f)

    location_name = data[0]['text']
    location_description = data[1]['text']
    skills = data[2]['text']
    characters = data[3]['text']

    main_loop_prompt += 'Here are the location name, description, skills, and characters:\n'
    main_loop_prompt += f'{location_name}\n'
    main_loop_prompt += f'{location_description}\n'
    main_loop_prompt += f'{skills}\n'
    main_loop_prompt += f'{characters}\n\n'

    ## now, add the history
    main_loop_prompt += '''Here is the history of the game thus far:
Each of these, except for the last, is a summary of what happened.
The last is the full text. What you output should be more like the full text.\n\n'''

    history = load_history_summary(game_id)

    # remove the last human message
    if history[-1]['writer'] == 'human':
        history = history[:-1]
    
    # remove the last AI message
    if history[-1]['writer'] == 'ai':
        history = history[:-1]

    # add the last full text AI response
    for item in frontend_history[::-1]:
        if item['writer'] == 'ai':
            history.append(item)
            break
    
    # then, add the user input and some gentle encouragement
    history.append({'writer': 'human', 'text': f'{user_input}. Remember - when in doubt, make something surprising and exciting happen!'})

    # check the history, and fix it if necessary
    history_fixed = fix_summary_history(history)

    def generate_response():
        response = ''
        for chunk in prompt(history_fixed, context='main_loop', system=main_loop_prompt, stream=True):
            response += chunk
            yield chunk
        
        # save the response to file
        save_text(game_id=game_id, text=response, writer='ai')

        # summarize the response
        summary = summarize(response, target_words=config.llm['summarization_target_word_count'])

        # save it to file
        save_text(game_id=game_id, text=summary, writer='ai', type='summaries')

    
    return StreamingHttpResponse(generate_response(), content_type='text/plain')



    




