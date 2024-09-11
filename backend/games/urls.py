from django.urls import path, include
from rest_framework import routers

import games.views as views

# router
router = routers.DefaultRouter()
router.register(r'characters', views.CharacterViewSet, 'characters')
router.register(r'skills', views.SkillViewSet, 'skills')



urlpatterns = [
    path('api/', include(router.urls)),
    path('get_current_version/', views.get_current_version),

    # game initialization
    path('initialize_game_key/', views.initialize_game_key),
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