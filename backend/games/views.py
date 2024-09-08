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
from games.gameplay import main_loop

from prompting import prompt

from games.save_game import save_text


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
@api_view(['POST'])
def initialize_game_key(request):
    '''
    Creates a game, and a unique UUID for it, then returns the key for the user to have. 
    '''

    dev = request.data['dev']
    if dev == 'true':
        time.sleep(1)
        return JsonResponse({
            'save_key': '0a8b6884-3e52-45f9-b560-4ce566200c3d', 
            'game_id': 140})

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
        time.sleep(2)
        return JsonResponse({'title': "The Curious Encounter of Baggins and Bigfoot"})

    # generate the title
    title = create_scenario_title(theme=theme, timeframe=timeframe, details=details)

    # update the game with this info
    game = Game.objects.get(id=game_id)
    game.theme = theme
    game.timeframe = timeframe
    game.starting_details = details
    game.title = title
    game.save()

    # save the title to file
    save_text(game_id=game_id, text=title, writer='ai')

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
        with open('/Users/jimbo/Documents/coding/projects/survival-game/backend/game_files/142/full_text/0.json', 'r') as f:
            data = json.load(f)

            def generate_response():
                for char in data[1]['text']:
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
            with open('/Users/jimbo/Documents/coding/projects/survival-game/backend/game_files/142/full_text/0.json', 'r') as f:
                data = json.load(f)

                for char in data[2]['text']:
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

        # iterate through the crash story
        for chunk in create_wakeup(crash_story, location_description, skills, characters,
                                title=game.title, theme=game.theme,
                                timeframe=game.timeframe, details=game.starting_details):
            wakeup_story += chunk
            yield chunk
        
        # save the crash story to file
        save_text(game_id=game_id, text=wakeup_story, writer='ai')


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

Speaking of the right of the screen - in the bottom right you should see a button that says 'Key'. 
Click it.

So - what will you do next?'''
    
    # stream back the response
    def generate_response():
        for chunk in intro:
            time.sleep(0.0005)
            yield chunk


    return StreamingHttpResponse(generate_response(), content_type='text/plain')

@csrf_exempt
@api_view(['POST'])
def main_loop(request):
    '''
    The main loop of the game.
    '''

    game_id = request.data['game_id']
    history = request.data['history']
    user_input = request.data['user_input']

    dev = request.data['dev']
    if dev == 'true':
        time.sleep(1)
        with open('/Users/jimbo/Documents/coding/projects/survival-game/backend/game_files/142/full_text/0.json', 'r') as f:
            data = json.load(f)

            def generate_response():
                for char in data[1]['text']:
                    time.sleep(0.01)
                    yield char

            return StreamingHttpResponse(generate_response(), content_type='text/plain')

    # remove the game intro from the history
    history = [item for item in history if item['writer'] != 'game_intro']

    ## first, add the theme, timeframe, and details to the system prompt
    game = Game.objects.get(id=game_id)
    
    main_loop_prompt = 'Here are the theme, timeframe, and details of the game:\n'

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

    main_loop_prompt += 'Here is the history of the game thus far:\n\n'

    # add the user input to the history
    history.append({'writer': 'human', 'text': f'{user_input}. Remember - when in doubt, make something surprising and exciting happen!'})

    # add a human message before the crash story
    history.insert(0, {'writer': 'human', 'text': 'Start the story for me - have them crash land.'})

    # add a human message before the wakeup story
    history.insert(2, {'writer': 'human', 'text': 'Now tell the story of them waking up in this new, strange place.'})

    def generate_response():
        response = ''
        for chunk in prompt(history, context='main_loop', system=main_loop_prompt, stream=True):
            response += chunk
            yield chunk
        
        # save the crash story to file
        save_text(game_id=game_id, text=response, writer='ai')
    
    return StreamingHttpResponse(generate_response(), content_type='text/plain')








