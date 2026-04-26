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

    
    try:
        # fetches the html of the given url & stops fetching when the timeout seconds is reached
        res = requests.get(url, timeout=5)

    # proceeds only if the error is caused by Timeout, ConnectionError, HTTPError etc
    except requests.exceptions.RequestException:
        try:
            # refresh the website and try once more   
            res = requests.get(url, timeout=5)
        except requests.exceptions.RequestException:
            return {"error": "Request failed twice"}
        
    # 200 is for success
    if res.status_code != 200:          
        return {"error": "Failed to fetch page"}
    
    # converts HTML into a structured data
    soup=BeautifulSoup(res.text,'html.parser')          

    # if title tag exists in the html
    if soup.title:     
        # stores the only the text inside the title tag, if anything other than simple sentences are present then it returns None     
        title=soup.title.string         
    else:                   
        title="No Title"
    
    # stores everything inside the <p> tag and inludes the tag itself too -> this will find each and every <p> and store it
    paragraphs=soup.find_all("p")       

    content=""
    # for eg: paragraph = [<p>First</p>, <p>Second</p>]
    for para in paragraphs[:5]:         
        if para.text.strip():
            content+= f"<p>{para.text}</p>"

    return {
        "title": title,
        "content": content
    }
