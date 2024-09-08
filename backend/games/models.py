from django.db import models

# Create your models here.


class Game(models.Model):
    '''A game.'''

    # save key for the game - given to the player when they start the game,
    # and used to access the game later
    save_key = models.UUIDField(null=True)

    # the title of the game - will be created by AI
    title = models.CharField(max_length=200, null=True)

    # theme of the game - a word or phrase
    theme = models.CharField(max_length=1000, null=True)

    # timeframe of the game - a phrase to signify what time period the game is set in
    ## ex: "medieval", "futuristic", "modern", "1960's"
    timeframe = models.CharField(max_length=1000, null=True)

    # starting details -- extra details that can be added into the story of the game
    starting_details = models.CharField(max_length=2000, null=True)

    # locations - the locations in the game
    ## many to many because I want to keep the option open for a location to be in multiple games
    ## if there are locations that are really good
    locations = models.ManyToManyField('Location')

    # characters - the characters in the game
    ## many to many because I want to keep the option open for a character to be in multiple games
    ## if there are characters that are really good
    characters = models.ManyToManyField('Character')

    # skills - the skills that are in the game
    ## many to many because I want to keep the option open for a skill to be in multiple games
    ## if there are skills that are really good
    skills = models.ManyToManyField('Skill')

    # total_cost keeps track of how much the game has cost to run, from LLM usage
    ## currently not keeping track of this - could do it in the future?
    #total_dollar_cost = models.FloatField(default=0.0)

    # word count - the total word count of the game
    word_count = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Location(models.Model):
    '''A location in a game.'''

    # name of the location
    name = models.CharField(max_length=200, null=True)

    # description of the location
    description = models.CharField(max_length=5000, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Character(models.Model):
    '''A character in a game.'''

    # name of the character
    name = models.CharField(max_length=200, null=True)

    # history of the character
    history = models.CharField(max_length=3000, null=True)

    # personality
    personality = models.CharField(max_length=3000, null=True)

    # physical description
    physical_description = models.CharField(max_length=3000, null=True)

    # skills - the skills, and the level of the skills, that the character has
    skills = models.JSONField(null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Skill(models.Model):
    ''' A skill that a character can have. '''

    # name of the skill
    name = models.CharField(max_length=200, null=True)

    # description of the skill
    description = models.CharField(max_length=3000, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
