from bs4 import BeautifulSoup
from modules.common import *
from math import ceil
import requests
import os
import time

MODULE_NAME = os.path.basename(__file__).replace(".py", "")
NUMBER_OF_BEERS_PER_PAGE = 36

def run():
    """The main function of the module."""
    log_and_print(get_lang_text("BROWSE_ONLY"))
    list = []

    # The script will crawl enough pages to retrieve the specified amount of beers.
    for page_number in range(1, ceil(ARGS.beercount / NUMBER_OF_BEERS_PER_PAGE) + 1):
        crawl("https://www.csakajosor.hu/index.php?route=product/list&sort=p.date_available&order=DESC&latest=16&page={}".format(page_number), list)

    # Sets the value for the new_entries list in case it's a first run.
    new_entries = list

    # If it's not a first run compares the previous beer list with the current one.
    if is_path_exists("json/{}.json".format(MODULE_NAME)):
        old_json = read_json("json/" + MODULE_NAME)
        new_entries = get_new_entries(old_json, list)

    # Writes the new beer list into the shops json file.
    write_json(list, "json/" + MODULE_NAME)

    return new_entries

def crawl(url, list):
    """Creates a list of Beer objects."""
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    print(end='', flush=True)

    for element in soup.find_all("a", "img-thumbnail-link"):

        # If the set amount of beer is gathered breaks the crawl loop.
        if ARGS.beercount == len(list):
            break

        # If for some reason there is no link to go to the beers page, skips to the next element.
        if 'href' not in element.attrs:
            continue

        try_counter = 0

        # Tries the crawl up to three times to eliminate breaks caused by network errors.
        while try_counter < 3:
            try:
                sub_soup = BeautifulSoup(requests.get(element['href']).text, "html.parser")
                beer = Beer()

                beer.link = element['href']
                beer.abv = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-alkoholfok"), "text")
                beer.style = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-tipus"), "text")
                beer.package = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-urtartalom"), "text") + " " + get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-kiszereles"), "text")
                beer.country = get_element_attribute(get_element(sub_soup, "td", "param-value featured-param-label featured-orszag"), "text")
                beer.brewery = get_element_attribute(get_element_attribute(get_element(sub_soup, "tr", "product-parameter-row manufacturer-param-row"), "span"), "text")
                beer.name = get_formatted_name(get_element_attribute(get_element(sub_soup, "h1", "page-head-title product-page-head-title position-relative"), "text"), beer.brewery)
                beer.price = get_tag_attribute(get_element(get_element(sub_soup, "div", "product-page-price-line"), "meta", itemprop="price"), "content") 
                beer.currency = get_tag_attribute(get_element(get_element(sub_soup, "div", "product-page-price-line"), "meta", itemprop="pricecurrency"), "content")
                try_counter = 3
            except KeyboardInterrupt:
                raise
            # If there was an error sleeps for five seconds and adds one to the try_counter.
            except:
                time.sleep(5)
                try_counter = try_counter + 1

        list.append(beer.__dict__)
        print(".", end='', flush=True)