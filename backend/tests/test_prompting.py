
import pytest
import config

from games.prompting import prompt, prompt_stream
from anthropic.lib.streaming._prompt_caching_beta_types import MessageStopEvent as CacheMessageStopEvent
from anthropic.lib.streaming._prompt_caching_beta_types import TextEvent as CacheTextEvent


@pytest.fixture
def mock_config(mocker):
    mocker.patch.dict(config.llm, {
        'provider': 'ANTHROPIC',
        'prompts_path': 'dummy_path',
        'api_key': 'dummy_api_key',
        'model': 'dummy_model'
    })
    mocker.patch('games.utils.load_yaml', return_value={
        'main': 'Main prompt text.',
        'context': 'Context-specific prompt text.'
    })

@pytest.fixture
def mock_anthropic_client(mocker):
    mock_client = mocker.Mock()
    mocker.patch('anthropic.Anthropic', return_value=mock_client)
    return mock_client

def test_prompting(mocker, mock_config, mock_anthropic_client):

    mock_calculate_price = mocker.patch('games.prompting.calculate_price', return_value=0.01)

    mock_message = mocker.Mock()
    mock_message.content = [mocker.Mock(text='Response text')]
    mock_message.usage.input_tokens = 100
    mock_message.usage.output_tokens = 50
    mock_message.usage.cache_creation_input_tokens = 20
    mock_message.usage.cache_read_input_tokens = 10
    mock_anthropic_client.beta.prompt_caching.messages.create.return_value = mock_message

    message = 'Test message'
    text, cost = prompt(message, context='create_crash', caching=True)

    assert text == 'Response text'
    assert cost == 0.01
    mock_anthropic_client.beta.prompt_caching.messages.create.assert_called_once()
    mock_calculate_price.assert_called_once_with('dummy_model', {
        'input_tokens': 100,
        'output_tokens': 50,
        'cache_input_tokens': 20,
        'cache_read_tokens': 10
    }, caching=True)

def test_prompt_with_list_message(mocker, mock_config, mock_anthropic_client):
    mock_calculate_price = mocker.patch('games.prompting.calculate_price', return_value=0.01)
    mock_message = mocker.Mock()
    mock_message.content = [mocker.Mock(text='Response text')]
    mock_message.usage.input_tokens = 100
    mock_message.usage.output_tokens = 50
    mock_message.usage.cache_creation_input_tokens = 20
    mock_message.usage.cache_read_input_tokens = 10
    mock_anthropic_client.beta.prompt_caching.messages.create.return_value = mock_message

    message = [{'writer': 'user', 'text': 'User message'}, {'writer': 'ai', 'text': 'AI message'}]
    text, cost = prompt(message, context='create_crash', caching=True)

    assert text == 'Response text'
    assert cost == 0.01
    mock_anthropic_client.beta.prompt_caching.messages.create.assert_called_once()
    mock_calculate_price.assert_called_once_with('dummy_model', {
        'input_tokens': 100,
        'output_tokens': 50,
        'cache_input_tokens': 20,
        'cache_read_tokens': 10
    }, caching=True)