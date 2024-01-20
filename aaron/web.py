# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/web.ipynb.

# %% auto 0
__all__ = ['clean_text', 'request', 'handle_response', 'ddg']

# %% ../nbs/web.ipynb 3
import re
from bs4 import BeautifulSoup

# %% ../nbs/web.ipynb 4
def clean_text(soup: BeautifulSoup) -> str:
    import re
    from bs4 import BeautifulSoup
    """Extracts text from html whilst removing extra whitespace and newlines"""
    text = soup.get_text()
    text = re.sub(r'^\s*$', '\n', text, flags=re.MULTILINE) # convert any white space only lines to newlines
    text = re.sub(r'\n{3,}', '\n\n', text) # squish any 3 or more consecutive newlines to 2 newlines
    return text 

# %% ../nbs/web.ipynb 7
from pathlib import Path

# %% ../nbs/web.ipynb 8
async def request(url: str=None, search: str=None, browser="brave") -> str:
    from playwright.async_api import async_playwright
    # if we are inside a Jupyter notebook, we have to patch the event loop
    if "get_ipython" in globals():
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError as e:
                e.args.append("Detected we are inside a IPython or Jupyter environment. Import requires access to an event loop. Please install nest_asyncio to enable this functionality")
                raise e
                
    if browser == "brave":
        brave = Path("/usr/bin/brave-browser")
        

    async with async_playwright() as p:
        if browser == "brave":
            browser = await p.chromium.launch(headless=True, executable_path=brave)
        else:
            browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        if url:
            await page.goto(url)
        elif search:
            await page.goto("https://duckduckgo.com")
            await page.click('input[name="q"]')
            await page.type('input[name="q"]', search)
            await page.press('input[name="q"]', "Enter")
        await page.wait_for_load_state("networkidle")
        content = await page.content()
        await browser.close()
        return content

# %% ../nbs/web.ipynb 12
from pathlib import Path
import asyncio
import json
from playwright.async_api import async_playwright


# %% ../nbs/web.ipynb 13
async def handle_response(response, data):
    if "links.duckduckgo.com/d.js" in response.url:
        d = await response.body()
        d = str(d)
        # by inspection, we know the data lives between these two function calls
        s = str(d).find("DDG.pageLayout.load(\\'d")
        e = str(d).find("DDG.duckbar.load(\\'images")
        d = d[s:e]
        # after finding the location of the data, we extract out the relevant json
        s = d.find("[")
        e = d.rfind("]") + 1
        d = d[s:e].encode("utf-8").decode("unicode_escape")
        d = json.loads(d)
        d = [[r.get("u"), r.get("t"), r.get("a")] for r in d if r.get("a")]
        data.set_result(d)

async def ddg(q, wait=1, browser="brave", headless=True):
    # if we are inside a Jupyter notebook, we have to patch the event loop
    if "get_ipython" in globals():
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError as e:
                e.args.append("Detected we are inside a IPython or Jupyter environment. Import requires access to an event loop. Please install nest_asyncio to enable this functionality")
                raise e
                
    if browser == "brave":
        brave = Path("/usr/bin/brave-browser")
    async with async_playwright() as p:
        if browser == "brave":
            browser = await p.chromium.launch(headless=headless, executable_path=brave)
        else:
            browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        data = asyncio.Future()
        page.on("response", lambda response: asyncio.create_task(handle_response(response, data)))
        await page.goto("https://duckduckgo.com")
        await page.click('input[name="q"]')
        await page.type('input[name="q"]', q)
        await page.press('input[name="q"]', "Enter")
        data = await data
        content = await page.content()
        # await page.wait_for_load_state("networkidle")
        if wait:
            await asyncio.sleep(wait)
        print(data)
        print()
        print(content)
        return data, content


# %% ../nbs/web.ipynb 17
from httpx import AsyncClient
from playwright.async_api import async_playwright
import asyncio

# %% ../nbs/web.ipynb 18
# `nest_asyncio` allows asyncio to run nested event loops, which is often necessary
# in a Jupyter notebook because the kernel itself is running an event loop.
# Without this, using asyncio-based libraries like httpx or aiohttp can cause errors.
if "get_ipython" in globals():
    try:
        import nest_asyncio

        nest_asyncio.apply()
    except ImportError as e:
        raise ImportError(
            "Detected we are inside a IPython or Jupyter environment."
            "Import requires access to an event loop."
            "Please install nest_asyncio to enable this functionality"
        ) from e