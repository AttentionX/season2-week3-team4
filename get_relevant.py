import openai_api

chatgpt = "gpt-3.5-turbo"
gpt4 = 'gpt-4'
openai_api = openai_api.OpenAI_API(model=chatgpt)

def get_prompt(text, company):
    prompt = f"""
    You are given noisy texts crawled from the web. They are about the stock trends of the company {company}.
    Not all the information is relevant. You should find relevant information and predict the stock prices.
    Return your answer in the following format.
    
    Answer: <Rise/Fall>
    Reason: <Your reason>

    """
    return prompt

def get_relevant(text, company):
    # Answer question via retrieved chunks
    response = openai_api.chatgpt(get_prompt(text,company))
    return response