import pytest
import os
import yaml
from games.utils import load_yaml, add_info_to_initialization_prompt, get_gamefile_listdir, get_file_size, check_file_exists
import config

@pytest.fixture
def mock_config_env_dev(mocker):
    mocker.patch.dict(os.environ, {'ENV': 'DEV'})
    mocker.patch('config.ENV', 'DEV')

@pytest.fixture
def mock_config_env_prod(mocker):
    mocker.patch.dict(os.environ, {'ENV': 'PROD'})
    mocker.patch('config.ENV', 'PROD')

def test_load_yaml(mocker):
    mock_open = mocker.mock_open(read_data="key: value")
    mocker.patch("builtins.open", mock_open)
    result = load_yaml("dummy_path.yaml")
    assert result == {"key": "value"}

def test_add_info_to_initialization_prompt():
    result = add_info_to_initialization_prompt("Fantasy", "Medieval", "Dragons, Magic", "Welcome to the game.")
    assert result == "Welcome to the game. The theme is Fantasy. The timeframe is Medieval. The following details will be incorporated into the scenario: Dragons, Magic."

def test_get_gamefile_listdir_dev(mocker, mock_config_env_dev):
    mocker.patch("os.listdir", return_value=["1.json", "2.json", "not_a_game.txt"])
    result = get_gamefile_listdir("dummy_path")
    assert result == ["1.json", "2.json"]

def test_get_file_size_dev(mocker, mock_config_env_dev):
    mocker.patch("os.path.getsize", return_value=1024)
    result = get_file_size("dummy_path")
    assert result == 1024

def test_check_file_exists_dev(mocker, mock_config_env_dev):
    mocker.patch("os.path.exists", return_value=True)
    result = check_file_exists("dummy_path")
    assert result is True
