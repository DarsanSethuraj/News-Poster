from fastapi import FastAPI
from fastapi import Query
import requests
from bs4 import BeautifulSoup

# cd "Backend-for-Auto-News-Post"
# uvicorn main:app --reload

# http://127.0.0.1:8000/test

app = FastAPI()

@app.get("/test")
def test():
    return {"message": "Backend working 🚀"}

@app.get("/news")
def FetchTitleAndPara(url: str = Query(...)):         

    # so that websites don't block my request thinking its bot
    headers = {"User-Agent": "Mozilla/5.0"} 
    
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

    if soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True)
    else:
        title = "No Title"

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

    # CREATE THE BANNED PHRASES IN LOWERCASE
    banned_phrases = [
    "advertisement",
    "read more",
    "categories:",
    "tags:",
    "share this:",
    "related articles",
    "uncategorized",
    "listen to the latest"
    ] 

    content=""
    # for eg: paragraph = [<p>First</p>, <p>Second</p>]
    for para in paragraphs:   

        # to remove image captions
        if para.find_parent(["figure", "figcaption"]):
            continue

        # gets the content inside the HTML tags
        text = para.get_text(" ", strip=True)

        if not text:
            continue

        #if para has less than 10 characters
        if len(text) < 10:
            continue
        
        if any(phrase in text.lower() for phrase in banned_phrases):
            continue
    
        content += f"<p>{text}</p>"

    return {
        "title": title,
        "content": content
    }
