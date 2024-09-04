

class Game:

    def __init__(self):

        self.locations = []

        self.starting_scenario = None

        self.skills = {}


class Location:

    def __init__(self, name, description):

        self.name = name
        self.description = description

        
        
def initialize_game():
    '''Initialize the game.'''

    