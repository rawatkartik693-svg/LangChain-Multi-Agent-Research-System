from langchain.tools import tool 
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient # create tavily as custom tool for web search
from rich import print  # give 5 statement but not clear enough to give answer to question.
                        # need tool rich  helps us  to se  good print statemnt also use logging /debugging

from bs4 import BeautifulSoup    # for second tool 
from readability import Document #
import trafilatura  #  with beautiful soup dependency package 
import re  # regular expression


load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str: # take query use tavily to search web and return results
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = tavily.search(query=query,max_results=5)


    out = []  # 5 outputs appending in empty list five link respnse means 

    for r in results['results']: # running for lop this result have result keywoard going inside this is a json resp taking 3 things 
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )  # instead of taking full content take title,url and content (300 words) for agent  1  understand to answer question and also use rich print in result -only 3 things need url,title ,content for agent 1
    
    return "\n----\n".join(out) # join give new line and join


   # print(results)  # now use rich print in result -only 3 things need url,title ,content for agent 1 



@tool  # func generated from chat gpt /     gave decorater so invokeS operation  can do 
def scrape_url(url: str) -> str:  # it takes a url and scrap all  content from url,it perform scrapping,# this func go to particular url  and extract all relevent content and then use by next agent
    """                          
    Scrape and extract clean readable content from a URL.
    Uses multiple extraction strategies for better reliability.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        # ── Fetch page ─────────────────────────────────────
        response = requests.get(   # using  req package hitting url 
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        html = response.text # after that get  html resp 

        # ──────────────────────────────────────────────────
        # Strategy 1 → trafilatura (BEST for articles/blogs)
        # ──────────────────────────────────────────────────
        extracted = trafilatura.extract(   # extract content everything happen with help of beautiful soup
            html,
            include_comments=False,
            include_tables=False
        )

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', extracted)
            return cleaned[:5000]

        # ──────────────────────────────────────────────────
        # Strategy 2 → readability
        # ──────────────────────────────────────────────────
        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', text)
            return cleaned[:5000]

        # ──────────────────────────────────────────────────
        # Strategy 3 → fallback full page extraction
        # ──────────────────────────────────────────────────
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        cleaned = re.sub(r'\s+', ' ', text)

        if cleaned:
            return cleaned[:5000] # if get content return cleaned

        return "Could not extract meaningful content from the page."  # nt get content exception raise , imp when using third party services

    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."

    except requests.exceptions.HTTPError as e:
        return f"HTTP error occurred: {str(e)}"

    except Exception as e:
        return f"Could not scrape URL: {str(e)}"