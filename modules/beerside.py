from bs4 import BeautifulSoup, ResultSet
from modules.common import *
import requests
import os
import time

MODULE_NAME = os.path.basename(__file__).replace(".py", "")

def run():
    log_and_print(get_lang_text("BROWSE_BEERSIDE"))
    list = crawl("https://www.beerside.hu/SHOP07.html")
    new_entries = list

    if is_json_exists("json/" + MODULE_NAME):
        old_json = read_json("json/" + MODULE_NAME)
        new_entries = get_new_entries(old_json, list)
       
    write_json(list,"json/" +  MODULE_NAME)
    return new_entries

def crawl(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    list = []
    print(end='', flush=True)

    elements = soup.find_all("a", "butt_reszletes")

    for i in range(0, min(ARGS.maximumbeer, len(elements))):

        element = elements[i]
        
        if 'href' not in element.attrs:
            continue

        try_counter = 0

        while try_counter < 3:
            try:
                sub_soup = BeautifulSoup(requests.get("https://www.beerside.hu" + element['href']).text, "html.parser")
                beer = Beer()

                beer.link = "https://www.beerside.hu" + element['href']
                set_attributes(sub_soup, beer)
                set_price_and_currency(sub_soup, beer)
                beer.country = NotAvailable.text
                beer.brewery = NotAvailable.text
                beer.name = get_formatted_name(get_element_attribute(get_element(sub_soup, "h1", itemprop="name"), "text"), beer.brewery)
                try_counter = 3
            except KeyboardInterrupt:
                raise
            except:
                time.sleep(5)
                try_counter = try_counter + 1

        list.append(beer.__dict__)
        print(".", end='', flush=True)

    return list

def set_attributes(sub_soup, beer):
    elements = get_elements(get_element(sub_soup, "table", "shop_attributes"), "td")
    size = len(elements)
    
    if size > 1 and isinstance(elements, ResultSet):
        beer.package = get_element_attribute(elements[0], "text").replace(" ", "")

        if size == 2:
            beer.abv = re.search(r'[0-9]*\,*\.*[0-9]+[%]{1}', get_element_attribute(get_element(sub_soup, "h1", itemprop="name"), "text")).group(0).strip()
            beer.style = get_element_attribute(elements[1], "text")
        else:
            beer.abv = get_element_attribute(elements[1], "text").replace(" ", "")
            beer.style = get_element_attribute(elements[2], "text")
    else:
        beer.package= NotAvailable.text
        beer.abv = NotAvailable.text
        beer.style = NotAvailable.text

def set_price_and_currency(sub_soup, beer):
    price_and_currency = get_element_attribute(get_element(sub_soup, "div", "termekar"), "text")
    
    if price_and_currency == NotAvailable.text:
        beer.price = NotAvailable.text
        beer.currency = NotAvailable.text
    else:
        price_and_currency = price_and_currency.split("-")
        beer.price = price_and_currency[0].replace(" ", "").strip()
        beer.currency = price_and_currency[1].replace(" ", "").strip()