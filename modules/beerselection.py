from bs4 import BeautifulSoup
from modules.common import *
from math import ceil
import requests
import os
import time

MODULE_NAME = os.path.basename(__file__).replace(".py", "")
NUMBER_OF_BEERS_PER_PAGE = 20

def run():
    log_and_print(get_lang_text("BROWSE_BEERSELECTION"))
    list = []

    for page_number in range(1, ceil(ARGS.beercount / NUMBER_OF_BEERS_PER_PAGE) + 1):
        crawl("https://www.beerselection.hu/index.php?route=product/list&stockfilter=1&latest=40&page={}#content".format(page_number), list)

    new_entries = list

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
                beer.abv = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-alkoholfok"), "text")
                beer.style = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-tipus"), "text")
                beer.package = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-kiszereles"), "text")
                beer.country = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-szaramazas"), "text")
                beer.brewery = get_element_attribute(get_element_attribute(get_element(sub_soup, "tr", "product-parameter-row manufacturer-param-row"), "span"), "text")
                beer.name = get_formatted_name(get_element_attribute(get_element(sub_soup, "h1", "page-head-title product-page-head-title position-relative"), "text"), beer.brewery)
                beer.price = get_tag_attribute(get_element(get_element(sub_soup, "div", "product-page-price-line"), "meta", itemprop="price"), "content") 
                beer.currency = get_tag_attribute(get_element(get_element(sub_soup, "div", "product-page-price-line"), "meta", itemprop="pricecurrency"), "content")
                try_counter = 3
            except KeyboardInterrupt:
                raise
            except:
                time.sleep(5)
                try_counter = try_counter + 1

        list.append(beer.__dict__)
        print(".", end='', flush=True)