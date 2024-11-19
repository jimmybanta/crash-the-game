import pytest
from games.model_prices import calculate_price

def test_calculate_price_with_caching():
    model = 'claude-3-haiku-20240307'
    tokens = {
        'input_tokens': 1000,
        'output_tokens': 500,
        'cache_input_tokens': 200,
        'cache_read_tokens': 300
    }
    expected_price = (
        0.00000025 * 1000 +
        0.00000125 * 500 +
        0.0000003 * 200 +
        0.00000003 * 300
    )
    result = calculate_price(model, tokens, caching=True)
    assert result == pytest.approx(expected_price)

def test_calculate_price_without_caching():
    model = 'claude-3-5-sonnet-20240620'
    tokens = {
        'input_tokens': 1000,
        'output_tokens': 500,
        'cache_input_tokens': 200,
        'cache_read_tokens': 300
    }
    expected_price = (
        0.000003 * 1000 +
        0.000015 * 500
    )
    result = calculate_price(model, tokens, caching=False)
    assert result == pytest.approx(expected_price)

def test_calculate_price_invalid_model():
    model = 'invalid-model'
    tokens = {
        'input_tokens': 1000,
        'output_tokens': 500,
        'cache_input_tokens': 200,
        'cache_read_tokens': 300
    }
    with pytest.raises(KeyError):
        calculate_price(model, tokens, caching=True)
