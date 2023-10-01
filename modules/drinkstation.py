from bs4 import BeautifulSoup
from modules.common import *
import requests
import os
import re

MODULE_NAME = os.path.basename(__file__).replace(".py", "")

def run():
    print(get_lang_text("BROWSE_DRINKSTATION"))
    list = crawl("https://drinkstation.hu/craft-sorok?stockfilter=1&sort=p.date_available&order=DESC&page=1")
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
        beer.style = NotAvailable.text
        beer.country = NotAvailable.text
        beer.brewery = get_element_attribute(get_element_attribute(get_element(sub_soup, "tr", "product-parameter-row manufacturer-param-row"), "span"), "text")
        beer.price = get_tag_attribute(get_element(get_element(sub_soup, "div", "product-page-price-line"), "meta", itemprop="price"), "content") 
        beer.currency = get_tag_attribute(get_element(get_element(sub_soup, "div", "product-page-price-line"), "meta", itemprop="pricecurrency"), "content")
        break_down_name(sub_soup, beer)

        list.append(beer.__dict__)
        print(".", end='', flush=True)

    print()
    return list

def break_down_name(sub_soup, beer):
    name = get_element_attribute(get_element(sub_soup, "h1", "page-head-title product-page-head-title position-relative"), "text")

    try:
        beer.package = re.search(r'[0-9]+[m,M]{1}[l,L]{1}', name).group(0).strip()
    except:
        beer.package = NotAvailable.text

    try:
        beer.abv = re.search(r'[0-9]*\,*\.*[0-9]+[%]{1}', name).group(0).strip()
    except:
        beer.abv = NotAvailable.text

    beer.name = get_formatted_name(name, beer.brewery)