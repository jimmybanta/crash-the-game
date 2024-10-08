''' Functions to summarize text - for the purpose of increasing latency and decreasing costs from LLM API calls. '''

from games.decorators import retry_on_exception, catch_and_log
from games.prompting import prompt


@retry_on_exception(max_retries=3, delay=3)
def summarize(text, target_words=50):
    ''' 
    Uses the LLM to summarize text.

    Parameters
    ----------
    text : str
        The text to summarize.
    target_words : int
        The target number of words for the summary.

    Returns
    -------
    str
        The summary.
    float
        The cost to generate the summary.
    '''

    system_prompt = '''You are a summarization AI, working within the context of a storytelling game
in which a player is controlling a set a characters moving through a story. Each chunk of the story is long -
and you need to summarize it, so that these summaries can then be passed onto a Large Language Model to generate the
next part of the story in a way that is engaging and coherent.
Be on the lookout for important or interesting parts of the text, including anything a player says that could be important for later, 
and be sure to include them in your summary.\n'''

    summary_prompt = f"Summarize the following text in {target_words} words: \n\n {text}"

    # prompt the LLM for a summary and cost
    summary, cost = prompt(summary_prompt, 
                        system=system_prompt, stream=False, caching=False)
    

    return summary, cost

@catch_and_log
def fix_summary_history(history):
    '''
    Given a history of summaries, checks to make sure everything is formatted correctly.
    Mainly, checks that there are no consecutive 'ai' or 'human' texts, as the LLM can't accept these.
    If there are, it removes the first one.
    Also checks that there are no empty blocks.

    Parameters
    ----------
    history : list
        A list of dictionaries, each with a 'writer' and 'text' key.
    
    Returns
    -------
    list
        The corrected history
    '''

    new_history = []

    # check for consecutive 'ai' or 'human' texts
    for i, item in enumerate(history):

        # check for consecutive writers
        # if the writer is the same as the next item, then don't include it
        try:
            if item['writer'] == history[i + 1]['writer']:
                continue
        except IndexError:
            pass

        # check for empty text
        if item['text'] == '':
            item['text'] = 'continue'
        new_history.append(item)
    
    return new_history