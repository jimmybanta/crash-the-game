
''' Contains functions for prompting the LLM API. '''

import logging
import os
import anthropic

from anthropic.lib.streaming._prompt_caching_beta_types import MessageStopEvent as CacheMessageStopEvent
from anthropic.lib.streaming._prompt_caching_beta_types import TextEvent as CacheTextEvent
from anthropic.lib.streaming._types import MessageStopEvent as MessageStopEvent
from anthropic.lib.streaming._types import TextEvent as TextEvent

import config
from games.utils import load_yaml
from games.model_prices import calculate_price

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
    ''' Prompts the LLM API with a message, and returns the response. '''

    # the main prompt is always added in the system
    system_prompt = PROMPTS['main']

    # if we want to add something to the system prompt 
    ## depending on context of the game, then we can do that here
    if context:
        system_prompt += PROMPTS[context]
    
    # if there's additional system text to add
    if system:
        system_prompt += system

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
            if item['writer'] == 'ai':
                messages.append({
                    'role': 'assistant',
                    'content': [
                        {
                            'type': 'text',
                            'text': item['text']
                        }
                    ]
                })
                    
            elif item['writer'] == 'user':
                messages.append({
                    'role': 'user',
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
                messages[-3]['content'][0]['cache_control'] = {"type": "ephemeral"}
                messages[-5]['content'][0]['cache_control'] = {"type": "ephemeral"}
            except IndexError:
                pass

    # prompting from anthropic
    if PROVIDER == 'ANTHROPIC':

        # set up the client
        if not client:
            client = anthropic.Anthropic(api_key=config.llm['api_key'])
        
        
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

        if caching:
            parameters['system'][0]['cache_control'] = {"type": "ephemeral"}

        logger.info(f'Calling Anthropic API with stream={stream} and caching={caching}')

        if stream:
            
            return prompt_stream(parameters, client, 
                                 caching=caching,
                                 )
        
        else:
            if caching:
                message = client.beta.prompt_caching.messages.create(**parameters)

                text = message.content[0].text
                usage = message.usage

                tokens = {
                        'input_tokens': usage.input_tokens,
                        'output_tokens': usage.output_tokens,
                        'cache_input_tokens': usage.cache_creation_input_tokens,
                        'cache_read_tokens': usage.cache_read_input_tokens
                    }

                cost = calculate_price(config.llm['model'], tokens, caching=True)
                return text, cost
            else:
                message = client.messages.create(**parameters)
                
                text = message.content[0].text
                usage = message.usage

                tokens = {
                        'input_tokens': usage.input_tokens,
                        'output_tokens': usage.output_tokens,
                    }
                
                cost = calculate_price(config.llm['model'], tokens, caching=False)
                return text, cost

        
        
            


def prompt_stream(parameters, client, 
                  caching=True):
    ''' For streaming the prompt, when we don't want to wait for the whole response. '''

    if caching:
        with client.beta.prompt_caching.messages.stream(**parameters) as stream:
            for chunk in stream:
                # we're interested in two types of events
                # first - a text event
                if isinstance(chunk, CacheTextEvent):
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

    
if __name__ == '__main__':

    context = 'initialize_game'

    message = 'Create a game with the theme of cotton candy. Keep it very brief.'

    #for chunk in prompt(message, context=None, stream=True):
     #   print(chunk, end='')
    
    response = prompt(message, context=None, stream=False)

    print(response)
         
