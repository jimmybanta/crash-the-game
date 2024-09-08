
''' Contains functions for prompting the LLM API. '''

import config

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage

from utils import load_yaml

# get the llm provider
PROVIDER = config.llm['provider']

# load in the pre-written prompts, specific to that provider
PROMPTS = load_yaml(f'prompts/{PROVIDER}.yaml')

# instantiate the LLM
if PROVIDER == 'ANTHROPIC':
    MODEL = ChatAnthropic(model=config.llm['model'], api_key=config.llm['api_key'], max_tokens_to_sample=2048)




def prompt(message, 
           context=None, 
           system=None, 
           stream=False, 
           max_tokens=1024, 
           #caching=False, return_usage=False
           ):
    ''' Prompts the LLM API with a message, and returns the response. '''

    # TO DO LATER - add in prompt caching, for when prompts get longer (min prompt cache is 2048 tokens)
    # TO DO LATER - add in token usage tracking? for cost purposes

    # the main prompt is always added in the system
    system_prompt = PROMPTS['main']

    # if we want to add something to the system prompt 
    ## depending on context of the game, then we can do that here
    if context:
        system_prompt += PROMPTS[context]
    
    # if there's additional system text to add
    if system:
        system_prompt += system

    # set up the LLM chain
    prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt,),
        MessagesPlaceholder(variable_name="messages"),
        ]
    )

    chain = prompt_template | MODEL

    # if message is just a string, then send it as a human message
    if type(message) == str:
        messages = {'messages': [HumanMessage(content=message)]}
    # if message is a list, then there will be some AIMessages, some HumanMessages
    elif type(message) == list:
        messages = {'messages': []}
        for item in message:
            if item['writer'] == 'ai':
                messages['messages'].append(AIMessage(content=item['text']))
            elif item['writer'] == 'human':
                messages['messages'].append(HumanMessage(content=item['text']))

    # prompting from anthropic
    if PROVIDER == 'ANTHROPIC':

        if stream:
            return prompt_stream(messages, chain, 
                                 #return_usage=return_usage
                                 )
        
        else:
            response = chain.invoke(messages)
            return response.content

        
        
            


def prompt_stream(messages, chain, return_usage=False):
    ''' For streaming the prompt, when we don't want to wait for the whole response. '''

    for chunk in chain.stream(messages):
        yield chunk.content



    
if __name__ == '__main__':

    context = 'initialize_game'

    message = 'Create a game with the theme of cotton candy. Keep it very brief.'

    #for chunk in prompt(message, context=None, stream=True):
     #   print(chunk, end='')
    
    response = prompt(message, context=None, stream=False)

    print(response)
         
