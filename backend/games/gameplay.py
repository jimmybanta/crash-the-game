''' Functions for the main play of the game. '''

from prompting import prompt

def main_loop(user_input, history, system=None):
    '''
    The main loop of the game.
    '''

    # add the user input to the history
    history.append({'writer': 'human', 'text': user_input})

    print(history)

    prompt(history, context='main_loop', system=system, stream=True)

    pass
