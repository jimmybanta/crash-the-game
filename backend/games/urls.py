''' This file contains the URL patterns for the games app. '''

from django.urls import path, include
from rest_framework import routers
import django_eventstream.urls

import games.views as views

# router
router = routers.DefaultRouter()
router.register(r'characters', views.CharacterViewSet, 'characters')
router.register(r'skills', views.SkillViewSet, 'skills')



urlpatterns = [
    path('api/', include(router.urls)),

    # event stream
    #path('stream/', include(django_eventstream.urls), {'channels': ['game']}),
    path('stream/<game_id>/', include(django_eventstream.urls), 
         {'format-channels': ['game-{game_id}']}),

    # getting the current version
    path('get_current_version/', views.get_current_version),

    # game initialization
    path('initialize_save_key/', views.initialize_save_key),
    path('random_setup/', views.random_setup),
    path('initialize_game_title/', views.initialize_game_title),
    path('initialize_game_crash/', views.initialize_game_crash),
    path('initialize_game_wakeup/', views.initialize_game_wakeup),
    path('initialize_game_intro/', views.initialize_game_intro),

    # game loading
    path('load_game_info/', views.load_game_info),
    path('load_game/', views.load_game),

    # main gameplay
    path('main_loop/', views.main_loop),
]