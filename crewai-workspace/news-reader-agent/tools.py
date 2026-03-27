import time
from crewai.tools import tool
from crewai_tools import SerperDevTool
#브라우저를 컨트롤해서 스크랩할 목적
from playwright.sync_api import sync_playwright
#html 조작 목적
from bs4 import BeautifulSoup

search_tool = SerperDevTool( 
    n_results=30, 
) 

#테스트 목적으로 uv run tool.py 해서 호출결과만 보고싶을 시
#print(search_tool.run(search_query="Iran War"))

# param: agent가 읽어야 하는 웹사이트의 url
@tool 
def scrape_tool(url: str): 
    """ 
    Use this when you need to read the content of a website. 
    Returns the content of a website, 
    in case the website is not available, 
    it returns 'No content'. 
    Input should be a url string. 
    for example (https://www.reuters.com/world/asia-pacific/cambodia-thailand-begin-talks-malaysia-amid-fragile-ceasefire-2025-08-04/) 
    """ 
    
    print(f"Scrapping URL: {url}") 
    
    with sync_playwright() as p: 
        
        browser = p.chromium.launch(headless=True) 
        
        page = browser.new_page() 
        
        page.goto(url) 
        
        time.sleep(5) 
        
        html = page.content() 
        
        browser.close() 
        
        soup = BeautifulSoup(html, "html.parser") 
        
        unwanted_tags = [ 
            "header", 
            "footer", 
            "nav", 
            "aside", 
            "script", 
            "style", 
            "noscript", 
            "iframe", 
            "form", 
            "button", 
            "input", 
            "select", 
            "textarea", 
            "img", 
            "svg", 
            "canvas", 
            "audio", 
            "video", 
            "embed", 
            "object", 
        ] 
        
        for tag in soup.find_all(unwanted_tags): 
            tag.decompose() # 태그 통째로 제거
            
        content = soup.get_text(separator=" ") 
        
        return content if content != "" else "No content"