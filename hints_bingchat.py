import asyncio
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
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

    Here is the noisy text you should use.
    {text}

    """
    return prompt

def get_google_query(query):
    #raise NotImplementedError    
    return query + " stock price recent trend"

def get_webpage_text(page, link):
    page.goto(link, timeout=0)
    
    # Get webpage text
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract all text within the body tag
    text_content = soup.body.get_text()
    return text_content

async def playwright_init():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        while True:
            query = input("Enter your query: ")
            google_query = get_google_query(query)

            answer_texts = []
            
            # Could specify specific website for data source (Reddit, Wikipedia, etc)
            google_query_url = f"https://www.google.com/search?q={google_query}"
            page.goto(google_query_url)
            
            # page.type('input[name=q]', 'Your search query')
            # page.press('input[name=q]', 'Enter')
            
            page.wait_for_selector('.g')
            
            # Extract the top K links
            k = 5  # Choose the top K results
            links = page.eval_on_selector_all('.g', '''(results, k) => {
                return Array.from(results).slice(0, k).map(result => {
                    const anchor = result.querySelector('a');
                    return {
                        title: anchor.textContent,
                        href: anchor.href
                    };
                });
            }''', k)
            
            for link in links:
                text = get_webpage_text(page, link['href'])
                #print(text)
                answer_texts.append(text)

                # Get chunks and save to vectorDB
            
            with open(f"{google_query}.txt", "w") as f:
                for i, text in enumerate(answer_texts):
                    f.write(f"Rank {i}:\n")
                    f.write(f"{text}\n")

            # Answer question via retrieved chunks
            answer_text_joined = "\n".join(answer_texts)
            if openai_api.token_count(answer_text_joined) > 2000:
                answer_text_joined
            response = openai_api.chatgpt(get_prompt("\n".join(answer_texts), query))
            return response
            

if __name__ == "__main__":
    main()