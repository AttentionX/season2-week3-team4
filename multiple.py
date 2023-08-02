import numpy as np
import openai_api
from dotenv import load_dotenv
import sys
import os

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import openai_api

chatgpt = "gpt-3.5-turbo"
gpt4 = 'gpt-4'

openai_api = openai_api.OpenAI_API(model=chatgpt) #gpt4

# return [com1, com2, ...], [metric1, metric2, ...]
def compose_metric(user_prompt, article_num = 5):
    # extract company names
    prompt = f'''extract company numbers and names respectively from the sentence "{user_prompt}". Output only names, divided by comma, without explanation.'''
    response = openai_api.chatgpt(prompt)
    names = response.split(',')
    num_ = len(names)

    # m, n, p: recent stock price(list), recent property(list), article sentiments(list)
    #mets = []
   
    #for i in range(num_):
    #    mets.append([m, n, p])
   
   
    return names #, mets



def judge(name, met):
    def _linreg(f):
        x = np.array([i for i in range(len(f))])
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, f, rcond=None)[0]
        return m
   
    def _eval(x, y, z):
        x_, y_ = _linreg(x), _linreg(y)
        z_sum = sum(z)
        return np.sign(np.tanh(x_ + y_) + np.tanh(z_sum))
   
    if _eval(met[0], met[1], met[2]):
        return True
    else:
        return False


# return [com1_bool, com2_bool, ...]
def multiple(user_prompt, num = 5):
    com_name, metric = compose_metric(user_prompt, num)
    com_num = len(com_name)

    res = []

    for i in range(com_num):
        res.append(com_name[i], metric[i])

    return res 