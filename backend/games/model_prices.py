''' Function for calculating the price of an API call, given 
the model and usage data.'''


# dict with the prices of the models
models = {
    'claude-3-haiku-20240307': {
        'input_token_price': 0.00000025,
        'output_token_price': 0.00000125,
        'cache_input_token_price': 0.0000003,
        'cache_read_token_price': 0.00000003,
    }
}


def calculate_price(model, tokens, caching=True):
    '''
    Calculates the price of an LLM api call.

    Parameters
    ----------
    model : str
        The model to use.
    tokens : dict
        A dictionary with the number of tokens for each type.
    caching : bool
        Whether caching is enabled.

    Returns
    -------
    float
        The price of the API call.
    '''

    if caching:
        return (
            models[model]['input_token_price'] * tokens['input_tokens'] +
            models[model]['output_token_price'] * tokens['output_tokens'] +
            models[model]['cache_input_token_price'] * tokens['cache_input_tokens'] +
            models[model]['cache_read_token_price'] * tokens['cache_read_tokens']
            )
    else:
        return (
            models[model]['input_token_price'] * tokens['input_tokens'] +
            models[model]['output_token_price'] * tokens['output_tokens']
            )
