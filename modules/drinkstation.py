from bs4 import BeautifulSoup
from modules.common import *
from math import ceil
import requests
import os
import re
import time

MODULE_NAME = os.path.basename(__file__).replace(".py", "")
NUMBER_OF_BEERS_PER_PAGE = 200

def run():
    log_and_print(get_lang_text("BROWSE_DRINKSTATION"))
    list = []

    for page_number in range(1, ceil(ARGS.beercount / NUMBER_OF_BEERS_PER_PAGE) + 1):
        crawl("https://drinkstation.hu/craft-sorok?stockfilter=1&sort=p.date_available&order=DESC&page={}".format(page_number), list)

    if is_json_exists("json/" + MODULE_NAME):
        old_json = read_json("json/" + MODULE_NAME)
        new_entries = get_new_entries(old_json, list)

    write_json(list, "json/" + MODULE_NAME)
    return new_entries

def crawl(url, list):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    print(end='', flush=True)

    for element in soup.find_all("a", "img-thumbnail-link"):

        if ARGS.beercount == len(list):
            break

        if 'href' not in element.attrs:
            continue

        try_counter = 0

        while try_counter < 3:
            try:
                sub_soup = BeautifulSoup(requests.get(element['href']).text, "html.parser")
                beer = Beer()

                beer.link = element['href']
                beer.style = NotAvailable.text
                beer.country = NotAvailable.text
                beer.brewery = get_element_attribute(get_element_attribute(get_element(sub_soup, "tr", "product-parameter-row manufacturer-param-row"), "span"), "text")
                beer.price = get_tag_attribute(get_element(get_element(sub_soup, "div", "product-page-price-line"), "meta", itemprop="price"), "content") 
                beer.currency = get_tag_attribute(get_element(get_element(sub_soup, "div", "product-page-price-line"), "meta", itemprop="pricecurrency"), "content")
                break_down_name(sub_soup, beer)
                try_counter = 3
            except KeyboardInterrupt:
                raise
            except:
                time.sleep(5)
                try_counter = try_counter + 1

        list.append(beer.__dict__)
        print(".", end='', flush=True)

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