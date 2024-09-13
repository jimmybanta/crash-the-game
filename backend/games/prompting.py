
''' Contains functions for prompting the LLM API. '''

import logging
import os

import anthropic
from anthropic.lib.streaming._prompt_caching_beta_types import MessageStopEvent as CacheMessageStopEvent
from anthropic.lib.streaming._prompt_caching_beta_types import TextEvent as CacheTextEvent
from anthropic.lib.streaming._types import MessageStopEvent as MessageStopEvent
from anthropic.lib.streaming._types import TextEvent as TextEvent

import config

from games.model_prices import calculate_price
from games.utils import load_yaml


logger = logging.getLogger(__name__)


# get the llm provider
PROVIDER = config.llm['provider']

# load in the pre-written prompts, specific to that provider
PROMPTS = load_yaml(os.path.join(config.llm['prompts_path'], f'{config.llm["provider"].lower()}.yaml'))

def prompt(message, 
           context=None, 
           system=None, 
           stream=False, 
           client=None,
           max_tokens=1024, 
           caching=True, 
           ):
    ''' 
    Prompts the LLM API with a message.

    Parameters
    ----------
    message : str | list
        The message to prompt with. If a list, then it's a list of dictionaries
        with the writer and text of the message in each. 
        If it's a string, then it's just a message.
    context : str | None
        The context of the game in which the prompt is being made.
    system : str | None
        Additional system text to add to the prompt.
    stream : bool | False
        Whether to stream the prompt.
    client : anthropic.Anthropic | None
        The client to use for the prompt.
    max_tokens : int | 1024
        The maximum number of tokens to output.
    caching : bool | True
        Whether to use prompt caching.
    '''

    ## generate system prompt
    # the main prompt is always added to the system
    system_prompt = PROMPTS['main']

    # if we want to add something to the system prompt 
    # depending on context of the game, then we can do that here
    if context:
        system_prompt += PROMPTS[context]
    
    # if there's additional system text to add
    if system:
        system_prompt += system


    ## format the message
    # if message is just a string, then send it as a user message
    if type(message) == str:
        messages = [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': message
                    }
                ]
            }
        ]
    # if message is a list, then there will be some ai (assistant) messages, some user messages
    elif type(message) == list:
        messages = []
        for item in message:
            messages.append({
                'role': 'assistant' if item['writer'] == 'ai' else 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': item['text']
                    }
                ]
            })


        # setup caching
        if caching:
            try:
                # we set the 3rd from last and 5th from last with cache control
                ## we do this because, in the main loop, we don't want to cache the penultimate message
                ## because it is a full text message, while all the others are summaries
                ## we pass the full text message for continuity's sake, and to show the 
                ## LLM an example of the full text
                ## next turn, it will be replaced by its summary
                messages[-3]['content'][0]['cache_control'] = {"type": "ephemeral"}
                messages[-5]['content'][0]['cache_control'] = {"type": "ephemeral"}
            except IndexError:
                pass

    # prompting from anthropic
    if PROVIDER == 'ANTHROPIC':

        # set up the client
        if not client:
            client = anthropic.Anthropic(api_key=config.llm['api_key'])
        
        # define the parameters for the LLM call
        parameters = {
            'model': config.llm['model'],
            'max_tokens': max_tokens,
            'system': [
                {
                    'type': 'text',
                    'text': system_prompt,
                }
            ],
            'messages': messages
        }

        # if we're caching, then we want to cache the whole system prompt
        # the system prompt doesn't change while we're in the main loop of the game
        ## so we definitely want to cache it
        if caching:
            parameters['system'][0]['cache_control'] = {"type": "ephemeral"}

        logger.info(f'Calling Anthropic API with stream={stream} and caching={caching}')


        # if we're streaming the prompt
        # then return prompt_stream, which is a generator function
        if stream:
            return prompt_stream(parameters, client, 
                                 caching=caching,
                                 )
        else:
            if caching:
                message = client.beta.prompt_caching.messages.create(**parameters)

                # get the output text and usage data
                text = message.content[0].text
                usage = message.usage

                # calculate the cost of the message
                tokens = {
                        'input_tokens': usage.input_tokens,
                        'output_tokens': usage.output_tokens,
                        'cache_input_tokens': usage.cache_creation_input_tokens,
                        'cache_read_tokens': usage.cache_read_input_tokens
                    }
                cost = calculate_price(config.llm['model'], tokens, caching=True)
                # return the text and the cost
                return text, cost
            else:
                message = client.messages.create(**parameters)
                
                # get the output text and usage data
                text = message.content[0].text
                usage = message.usage

                # calculate the cost of the message
                tokens = {
                        'input_tokens': usage.input_tokens,
                        'output_tokens': usage.output_tokens,
                    }
                cost = calculate_price(config.llm['model'], tokens, caching=False)
                # return the text and the cost
                return text, cost

def prompt_stream(parameters, client, 
                  caching=True):
    ''' 
    Given parameters and a client, makes a streaming LLM call.

    Parameters
    ----------
    parameters : dict
        The parameters for the LLM call.
    client : anthropic.Anthropic
        The client to use for the call.
    caching : bool | True
        Whether to use prompt caching.

    Yields
    ------
    chunks : dict
        The chunks of the stream. All but one will be text chunks.
        The last one will be a message stop event, which will contain the cost of the message.
    '''

    if caching:
        with client.beta.prompt_caching.messages.stream(**parameters) as stream:
            for chunk in stream:
                # we're interested in two types of events

                # first - a text event
                if isinstance(chunk, CacheTextEvent):
                    # yield the text
                    yield { 'type': 'text', 'text': chunk.text }

                # second - the message stop event - this gives us the token usage
                ## and from that we can calculate the cost
                if isinstance(chunk, CacheMessageStopEvent):
                    
                    usage = chunk.message.usage
                    tokens = {
                        'input_tokens': usage.input_tokens,
                        'output_tokens': usage.output_tokens,
                        'cache_input_tokens': usage.cache_creation_input_tokens,
                        'cache_read_tokens': usage.cache_read_input_tokens
                    }

                    cost = calculate_price(config.llm['model'], tokens, caching=True)

                    # yield the cost
                    yield { 'type': 'message_stop', 'cost': cost }

    else:
        with client.messages.stream(**parameters) as stream:

            for chunk in stream:
                # we're interested in two types of events

                # first - a text event
                if isinstance(chunk, TextEvent):
                    yield { 'type': 'text', 'text': chunk.text }

                # second - the message stop event - this gives us the token usage
                ## and from that we can calculate the cost
                if isinstance(chunk, MessageStopEvent):
                    
                    usage = chunk.message.usage
                    tokens = {
                        'input_tokens': usage.input_tokens,
                        'output_tokens': usage.output_tokens,
                    }

                    cost = calculate_price(config.llm['model'], tokens, caching=False)

                    yield { 'type': 'message_stop', 'cost': cost }
