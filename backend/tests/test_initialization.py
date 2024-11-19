import pytest
import random
from games.initialization import random_setup, create_skills
import config
from games.utils import add_info_to_initialization_prompt


def test_random_setup(mocker):
    mocker.patch.dict(config.random_setup, {
        'themes': ['Fantasy', 'Sci-Fi'],
        'timeframes': ['Medieval', 'Future'],
        'details': ['Dragons', 'Magic', 'Spaceships', 'Aliens']
    })

    mock_random_choice = mocker.patch('random.choice', side_effect=['Fantasy', 'Medieval', 2, 'Dragons', 'Magic'])

    theme, timeframe, details = random_setup()

    assert theme == 'Fantasy'
    assert timeframe == 'Medieval'
    assert details == 'Dragons, Magic'
    assert mock_random_choice.call_count == 5