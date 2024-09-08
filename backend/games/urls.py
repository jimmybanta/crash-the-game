from django.urls import path, include

import games.views as views

""" from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'characters', views.CharacterViewSet) """


urlpatterns = [
    #path('api/', include(router.urls)),
    path('initialize_game_key/', views.initialize_game_key),
    path('initialize_game_title/', views.initialize_game_title),
    path('initialize_game_crash/', views.initialize_game_crash),
    path('initialize_game_wakeup/', views.initialize_game_wakeup),
    path('initialize_game_intro/', views.initialize_game_intro),
]