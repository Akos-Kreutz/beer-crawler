from bs4 import BeautifulSoup
from modules.common import *
from math import ceil
import requests
import os
import time

MODULE_NAME = os.path.basename(__file__).replace(".py", "")
NUMBER_OF_BEERS_PER_PAGE = 36

def run():
    log_and_print(get_lang_text("BROWSE_ONE"))
    list = crawl("https://onebeer.hu/sorok?infinite_page={}".format(ceil(ARGS.beercount / NUMBER_OF_BEERS_PER_PAGE) + 1))
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

    for element in soup.find_all("a", "product__name-link product_link_normal"):

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
                beer.abv = get_element_attribute(get_element(get_element(sub_soup, "div", {"id": "page_artdet_product_param_spec_3304722"}), "div", "artdet__spec-param-value"), "text").replace(" %", "%")
                beer.style = get_element_attribute(get_element(get_element(sub_soup, "div", {"id": "page_artdet_product_param_spec_3304707"}), "div", "artdet__spec-param-value"), "text")
                beer.package = get_element_attribute(get_element(get_element(sub_soup, "div", {"id": "page_artdet_product_param_spec_3304727"}), "div", "artdet__spec-param-value"), "text")
                beer.country = NotAvailable.text
                beer.brewery = get_element_attribute(get_element(get_element(sub_soup, "div", {"id": "page_artdet_product_param_spec_3304727"}), "div", "artdet__spec-param-value"), "text")
                beer.name = get_formatted_name(get_element_attribute(get_element(sub_soup, "h1", "artdet__name line-clamp--3-12 mb-0"), "text"), beer.brewery)

                price = get_element_attribute(get_element(sub_soup, "span", "artdet__price-discount product-price--sale"), "text")
                if price == NotAvailable.text:
                    price = get_element_attribute(get_element(sub_soup, "span", "artdet__price-base-value"), "text")

                beer.price = price.replace(" Ft", "").replace(" ", "")
                beer.currency = "Ft"
                try_counter = 3
            except KeyboardInterrupt:
                raise
            except:
                time.sleep(5)
                try_counter = try_counter + 1

        list.append(beer.__dict__)
        print(".", end='', flush=True)

    return list