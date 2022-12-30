import requests
import operator

from bs4 import BeautifulSoup
from functools import reduce

# global variables
BASE_URL = "https://www.amazon.com/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
           "Accept-Language": "en-US, en;q=0.9"}


# user defined functions
def getpage(query, url_type):
    """
    A helper function to create a BeautifulSoup object. Input query string and specify the url type.
    The goal is to return html code of a page.
    
    query: str input. Accepts search query by "item name" or "asin"
    
    url_type: specify the url type for the search you're doing. options = "item", "asin"
    """
    if url_type == "item":
        url = BASE_URL + "s?k=" + query
    elif url_type == "asin":
        url = BASE_URL + "product-reviews/" + query
    else:
        return "Error: url type unsupported. Choose from the following 'item', 'asin'"
        
    response = requests.get(url, headers = HEADERS)
    
    if response.status_code == 200:
        return BeautifulSoup(response.text, "html.parser")
    else:
        return "Error: status_code != 200"

    
def get_prod_name(query, start = 1, end = None):
    """
    query: string input. search items on amazon in browser url tab. 
    e.g. if you wanted to search for "iphone 13", it would be "iphone+13"

    start: integer input. starting page number, default = 1
    
    end: integer input. ending page number, default = None

    returns a list of product names from search
    """
    if end == None:
        query = query + f"&page={str(start)}"
        html_raw = getpage(query, "item")
        products = html_raw.find_all("span", class_ = "a-size-medium a-color-base a-text-normal")
        
        return list(map(lambda x: x.text, products))

    else:
        pages = range(start, end + 1)
        query = list(map(lambda x: query + f"&page={str(x)}", pages))
        html_raw = list(map(lambda x: getpage(x, "item"), query))
        html_tag = list(map(lambda x: x.find_all("span", class_ = "a-size-medium a-color-base a-text-normal"), html_raw))
        html_tag = reduce(operator.iconcat, html_tag) # flatten the ResultSet
        products = list(map(lambda x: x.text, html_tag))
        
        return products

    
def get_asin(query, start = 1, end = None):
    """
    ***NEED QUERY FORMAT ITEMS TO RETRIEVE ASIN***
    query: string input. search items on amazon in browser url tab. 
    e.g. if you wanted to search for "iphone 13", it would be "iphone+13"

    start: integer input. starting page number, default = 1
    
    end: integer input. ending page number, default = None

    returns a list of asin associated with the items from search
    """
    if end == None:
        query = query + f"&page={str(start)}"
        html_raw = getpage(query, "item")
        html_tag = html_raw.find_all("div", class_ = "s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16")
    
        return list(map(lambda x: x.attrs["data-asin"], html_tag))
    
    else:
        pages = range(start, end + 1)
        query = list(map(lambda x: query + f"&page={str(x)}", pages))
        html_raw = list(map(lambda x: getpage(x, "item"), query))
        html_tag = list(map(lambda x: x.find_all("div", class_ = "s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16"),
                            html_raw
                           )
                       )
        html_tag = reduce(operator.iconcat, html_tag) # flatten the ResultSet
        asin_list = list(map(lambda x: x.attrs["data-asin"], html_tag))

        return asin_list

    
def get_reviews(asin: list, start = 1, end = None):
    """
    asin: list input. a list of ASIN
    
    start: integer input. starting page number, default = 1
    
    end: integer input. ending page number, default = None
    
    returns individual review contents of a product-review page.
    """
    if end == None:
        query = list(map(lambda x: x + f"?pageNumber={str(start)}", asin))
        html_raw = list(map(lambda x: getpage(x, "asin"), query))
        html_tag = list(map(lambda x: x.find_all("span", attrs = {"data-hook": "review-body"}), html_raw))
        html_tag = reduce(operator.iconcat, html_tag) # flatten the ResultSet
        reviews = list(map(lambda x: x.text, html_tag))
        reviews = [r.strip("\n") for r in reviews]

        return reviews
    
    else:
        pages = range(start, end + 1)
        queries = []
                
        for p in pages:
            for id in asin:
                query = id + f"?pageNumber={str(p)}"
                queries.append(query)
        
        html_raw = list(map(lambda x: getpage(x, "asin"), queries))
        html_tag = list(map(lambda x: x.find_all("span", attrs = {"data-hook": "review-body"}), html_raw))
        html_tag = reduce(operator.iconcat, html_tag) # flattent the ResultSet
        reviews = list(map(lambda x: x.text, html_tag))
        reviews = [r.strip("\n") for r in reviews]
        
        return reviews
    

### test
# search_query = "iphone+14"
# print(get_prod_name(search_query, 1, 3))

# IDs = get_asin(search_query, 1, 3)
# print(get_reviews(IDs, 1, 3))