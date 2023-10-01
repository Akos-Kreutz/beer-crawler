from bs4 import BeautifulSoup
from modules.common import *
import requests
import os

MODULE_NAME = os.path.basename(__file__).replace(".py", "")

def run():
    print(get_lang_text("BROWSE_BEERSELECTION"))
    list = crawl("https://www.beerselection.hu/index.php?route=product/list&stockfilter=1&latest=40&page=1#content")
    new_entries = list

    if is_json_exists("json/" + MODULE_NAME):
        old_json = read_json("json/" + MODULE_NAME)
        new_entries = get_new_entries(old_json, list)
        
    write_json(list, "json/" + MODULE_NAME)
    return new_entries

def crawl(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    list = []
    print(end='', flush=True)

    for element in soup.find_all("a", "img-thumbnail-link"):

        if 'href' not in element.attrs:
            continue

        sub_soup = BeautifulSoup(requests.get(element['href']).text, "html.parser")
        beer = Beer()

        beer.link = element['href']
        beer.abv = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-alkoholfok"), "text")
        beer.style = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-tipus"), "text")
        beer.package = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-kiszereles"), "text")
        beer.country = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-szaramazas"), "text")
        beer.brewery = get_element_attribute(get_element_attribute(get_element(sub_soup, "tr", "product-parameter-row manufacturer-param-row"), "span"), "text")
        beer.name = get_formatted_name(get_element_attribute(get_element(sub_soup, "h1", "page-head-title product-page-head-title position-relative"), "text"), beer.brewery)
        beer.price = get_tag_attribute(get_element(get_element(sub_soup, "div", "product-page-price-line"), "meta", itemprop="price"), "content") 
        beer.currency = get_tag_attribute(get_element(get_element(sub_soup, "div", "product-page-price-line"), "meta", itemprop="pricecurrency"), "content")

        list.append(beer.__dict__)
        print(".", end='', flush=True)

    print()
    return list