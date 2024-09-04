
import random


class Character:

    '''A character in the game.'''

    def __init__(self, name):

        '''Initialize the character.'''

        self.name = name
        self.health = 100

        self.descriptions = {
            'physical': '',
            'personality': ''
        }

        self.inventory = {}

        self.relationships = {}

        self.health = {
            'physical': random.randint(50, 70),
            'mental': random.randint(50, 70),
            'hunger': random.randint(50, 70)
        }

def character_creator():