import os
import sys
import asyncio
from queue import Queue
from threading import Thread

from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
import openai
from dotenv import load_dotenv
from multiple import compose_metric

import tiktoken

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import openai_api

load_dotenv()

chatgpt = "gpt-3.5-turbo"
gpt4 = 'gpt-4'

openai_api = openai_api.OpenAI_API(model=gpt4)  # gpt4

# OpenAI API Key 세팅하기
openai.api_key = os.environ.get('OPENAI_KEY')


def clean_webtext(rawtext):
    cleaned_text = rawtext.replace("\n", "")
    return cleaned_text


def get_webpage_text(page, link):
    page.goto(link, timeout=0)

    # Get webpage text
    response = requests.get(link, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract all text within the body tag
    text_content = soup.body.get_text()
    return text_content


async def playwright_init():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()


def get_bingchat_result(query):
    """
    returns 5 retrieved text
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        google_query_url = f"https://www.google.com/search?q={query}"
        page.goto(google_query_url)
        print(f"went to {google_query_url}")

        page.wait_for_selector('.g', timeout=0)

        k = 2
        links = page.eval_on_selector_all('.g', '''(results, k) => {
            return Array.from(results).slice(0, k).map(result => {
                const anchor = result.querySelector('a');
                return {
                    title: anchor.textContent,
                    href: anchor.href
                };
            });
        }''', k)
        textList = []
        for link in links:
            text = get_webpage_text(page, link['href'])
            textList.append(clean_webtext(text))
        return textList


def main():
    query = input("Enter Company names: ")
    comp_names = compose_metric(query, 5)

    for comp in comp_names:
        textList = get_bingchat_result(comp + " 뉴스")

        enc = tiktoken.encoding_for_model("gpt-4")
        if len(enc.encode("\n".join(textList))) < 6000:
            textList = ["\n".join(textList)]

        print('asking to GPT model ...')
        summary = get_summary(comp, textList)
        prompt = f"아래는 {comp}에 대한 최신 정보입니다. 정보를 바탕으로 이 기업의 주식에 어떤 영향을 줄지 예측해주세요. \n\nInfo: \n{summary} \n\n 예측:"
        response = openai_api.chatgpt(prompt)
        print(response)


def get_summary(comp, text_list) -> str:
    queue = Queue()

    def thread_func(queue):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        queue.put(loop.run_until_complete(gpt_async(comp, text_list)))

    Thread(target=thread_func, args=(queue,)).start()
    return queue.get()


async def gpt_async(comp, text_list) -> str:
    tasks = []
    for t in text_list:
        prompt = f"아래는 {comp}에 대한 최신 정보입니다. 정보의 내용에 대해 긍정 부정을 판단하고, 아래의 요약문을 작성해주세요. \n\nInfo: \n{t} \n\n 요약문:"
        tasks.append(asyncio.get_event_loop().create_task(ask_to_gpt(prompt)))
    summarize_result = await asyncio.gather(*tasks)

    return ''.join(summarize_result)


async def ask_to_gpt(prompt):
    task = asyncio.get_event_loop().run_in_executor(None, openai_api.chatgpt, prompt)
    return await task



if __name__ == "__main__":
    main()
