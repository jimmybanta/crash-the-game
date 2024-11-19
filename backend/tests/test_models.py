import pytest
from games.models import Game, Location, Character, Skill
import uuid

@pytest.fixture
def create_location():
    return Location.objects.create(name="Forest", description="A dense forest.")

@pytest.fixture
def create_character():
    return Character.objects.create(name="Hero", history="A brave warrior.", personality="Courageous", physical_description="Tall and strong.", skills={"Swordsmanship": 5})

@pytest.fixture
def create_skill():
    return Skill.objects.create(name="Swordsmanship", description="The ability to wield a sword effectively.")

@pytest.fixture
def create_game(create_location, create_character, create_skill):
    game = Game.objects.create(
        save_key=uuid.uuid4(),
        title="Epic Adventure",
        theme="Fantasy",
        timeframe="Medieval",
        starting_details="Dragons, Magic",
        total_dollar_cost=10.0,
        turns=5,
        word_count=1000
    )
    game.locations.add(create_location)
    game.characters.add(create_character)
    game.skills.add(create_skill)
    return game

@pytest.mark.django_db
def test_game_creation(create_game):
    game = create_game
    assert game.title == "Epic Adventure"
    assert game.theme == "Fantasy"
    assert game.timeframe == "Medieval"
    assert game.starting_details == "Dragons, Magic"
    assert game.total_dollar_cost == 10.0
    assert game.turns == 5
    assert game.word_count == 1000
    assert game.created
    assert game.modified

@pytest.mark.django_db
def test_game_relationships(create_game, create_location, create_character, create_skill):
    game = create_game
    assert create_location in game.locations.all()
    assert create_character in game.characters.all()
    assert create_skill in game.skills.all()

@pytest.mark.django_db
def test_location_creation(create_location):
    location = create_location
    assert location.name == "Forest"
    assert location.description == "A dense forest."
    assert location.created
    assert location.modified

@pytest.mark.django_db
def test_character_creation(create_character):
    character = create_character
    assert character.name == "Hero"
    assert character.history == "A brave warrior."
    assert character.personality == "Courageous"
    assert character.physical_description == "Tall and strong."
    assert character.skills == {"Swordsmanship": 5}
    assert character.created
    assert character.modified

@pytest.mark.django_db
def test_skill_creation(create_skill):
    skill = create_skill
    assert skill.name == "Swordsmanship"
    assert skill.description == "The ability to wield a sword effectively."
    assert skill.created
    assert skill.modified