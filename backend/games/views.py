from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from uuid import uuid4

import config

from games.models import Game
from games.initialization import create_scenario_title, create_crash

from utils import calculate_price

# Create your views here.


@csrf_exempt
@api_view(['POST'])
def initialize_game_key(request):
    '''
    Creates a game, and a unique UUID for it, then returns the key for the user to have. 
    '''

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
    details = request.data['details']

    # generate the title
    title = create_scenario_title(theme=theme, details=details)

    # update the game with this info
    game = Game.objects.get(id=game_id)
    game.theme = theme
    game.starting_details = details
    game.title = title
    game.word_count += len(title.split())
    game.save()

    return JsonResponse({'title': title})


@csrf_exempt
@api_view(['POST'])
def initialize_game_crash(request):
    '''
    Given a game (which should now have a theme, details, and a title), 
    generates a crash scenario, to be sent back to the frontend.
    '''
    
    game_id = request.data['game_id']

    # get the game
    game = Game.objects.get(id=game_id)

    # generate the crash and return it as a streaming response
    response = StreamingHttpResponse(create_crash(title=game.title, theme=game.theme, details=game.starting_details), 
                                     content_type='text/plain')

    return response



