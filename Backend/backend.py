from fastapi import FastAPI
from fastapi import Query
import requests
from bs4 import BeautifulSoup
import re
import json

# cd "Backend-for-Auto-News-Post"
# uvicorn main:app --reload

# http://127.0.0.1:8000/test

app = FastAPI()

def get_bbc_image(soup):
    article = soup.find("article")

    if not article:
        return None

    imgs = article.find_all("img")

    for img in imgs:
        srcset = img.get("srcset")

        if not srcset:
            continue

        last_candidate = srcset.split(",")[-1].strip()

        return last_candidate.split()[0]

    return None

def get_news18_content(soup):
    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            data = json.loads(script.string)

            if isinstance(data, dict) and "articleBody" in data:
                return data["articleBody"]

        except:
            continue

    return None

def parse_news18_html(soup,banned_phrases):
    content = ""
    seen = set()

    start_tag = soup.find("figcaption")
    # Intro paragraph(s) before lastpara blocks
    intro_block = start_tag.find_next("div", string=lambda s: s and len(s.strip()) > 30)

    intro_blocks = [intro_block] if intro_block else []
    print("INTRO BLOCKS: ",intro_blocks)

    # Main article blocks
    article_blocks = soup.select("div.lastpara")
    print("ARTICLE BLOCKS: ",article_blocks)

    all_blocks = intro_blocks + article_blocks

    for block in all_blocks:
        text = block.get_text(" ", strip=True)

        if not text:
            continue

        lower = text.lower()

        if any(phrase in lower for phrase in banned_phrases):
                continue

        if lower.startswith("summary:"):
            break

        if lower == "advertisement":
            continue

        if "image credits:" in lower:
            continue

        if text in seen:
            continue

        seen.add(text)

        # Embedded tweet
        if block.find("blockquote", class_="twitter-tweet") or "pic.twitter.com" in text:
            content += f"<blockquote>{text}</blockquote>"
            continue

        # Strong heading with body underneath
        strong = block.find("strong")
        if strong:
            heading = strong.get_text(" ", strip=True)
            content += f"<h3>{heading}</h3>"

            remaining = text.replace(heading, "", 1).strip()
            if remaining:
                content += f"<p>{remaining}</p>"
            continue

        content += f"<p>{text}</p>"

    return content if content else None

@app.get("/test")
def test():
    return {"message": "Backend working 🚀"}

@app.get("/news")
def FetchTitleAndPara(url: str = Query(...)):         

    # so that websites don't block my request thinking its bot
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    try:
        # fetches the html of the given url & stops fetching when the timeout seconds is reached
        res = requests.get(url, headers=headers, timeout=5)
    
    

    # proceeds only if the error is caused by Timeout, ConnectionError, HTTPError etc
    except requests.exceptions.RequestException:
        try:
            # refresh the website and try once more   
            res = requests.get(url, headers=headers, timeout=5)
        except requests.exceptions.RequestException:
            return {"error": "Request failed twice"}
    
    # 200 is for success
    if res.status_code != 200:          
        return {"error": "Failed to fetch page"}
    
    # converts HTML into a structured data
    soup=BeautifulSoup(res.text,'html.parser')  
      

    # for getting title of the news
    if soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True)
    else:
        title = "No Title"


    # for getting feautured image of the news
    image_url = None

    if "bbc.com" in url:    # only for BBC
        image_url=get_bbc_image(soup)

    else:       # for every other site's image
        og_image = soup.find("meta", property="og:image")

        if og_image:
            image_url = og_image.get("content")
    

    
    # CREATE THE BANNED PHRASES IN LOWERCASE
    GLOBAL_BANNED_PHRASES = [
        "advertisement",
        "read more",
        "categories:",
        "tags:",
        "share this:",
        "related articles",
        "uncategorized",
        "listen to the latest",
        "additional reporting by",
        "sign up here",
        "our newsletter",
        "royal watch newsletter",
        "image credits:",
        "image credit:",
        "photo credit:",
        "photo credits:"
    ] 

    ASIANET_BANNED_PHRASES = [
        "asianet news",
        "malayalam news"
    ]

    MANORAMA_BANNED_PHRASES = [
        "ago"
    ]

    NEWS18_MALAYALAM_BANNED_PHRASES = [
        "ഇതും വായിക്കുക"
    ]

    banned_phrases=GLOBAL_BANNED_PHRASES.copy()
    
    if "asianetnews.com" in url:
        banned_phrases.extend(ASIANET_BANNED_PHRASES)

    elif "manoramaonline.com" in url:
        banned_phrases.extend(MANORAMA_BANNED_PHRASES)

    elif "malayalam.news18.com" in url:
        banned_phrases.extend(NEWS18_MALAYALAM_BANNED_PHRASES)


    # order in terms of priority (contents are mostly in one such tag) 
    possible_containers = [
    soup.find("article"),
    soup.find("main"),
    soup.find("div", class_="article-body"),
    soup.find("div", class_="post-content"),
    soup.find("div", class_="entry-content")]
    
    content_container = None
    
    for container in possible_containers:
        if container:
            content_container = container
            break
    
    if content_container:
        paragraphs = content_container.find_all("p")
    else:
        paragraphs = soup.find_all("p")  


    # for getting content out of news 18 malayalam
    if "news18.com" in url:
        content=parse_news18_html(soup,banned_phrases)

    
    else:
        content=""
        # for eg: paragraph = [<p>First</p>, <p>Second</p>]
        for para in paragraphs:   

            # to remove image captions
            if para.find_parent(["figure", "figcaption"]):
                continue

            # gets the content inside the HTML tags
            text = para.get_text(" ", strip=True)
            text = re.sub(r'\s+([.,!?;:])', r'\1', text)

            if not text:
                continue

            #if para has less than 10 characters
            if len(text) < 10:
                continue

            lower_text = text.lower()
            

            if any(phrase in lower_text for phrase in banned_phrases):
                continue
        
            content += f"<p>{text}</p>"

    return {
        "title": title,
        "content": content,
        "image_url": image_url
    }
