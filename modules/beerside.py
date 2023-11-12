from bs4 import BeautifulSoup, ResultSet
from modules.common import *
import requests
import os
import time

MODULE_NAME = os.path.basename(__file__).replace(".py", "")

def run():
    """The main function of the module."""
    log_and_print(get_lang_text("BROWSE_BEERSIDE"))
    list = crawl("https://www.beerside.hu/SHOP07.html")

    # Sets the value for the new_entries list in case it's a first run.
    new_entries = list

    # If it's not a first run compares the previous beer list with the current one.
    if is_path_exists("json/{}.json".format(MODULE_NAME)):
        old_json = read_json("json/" + MODULE_NAME)
        new_entries = get_new_entries(old_json, list)

    # Writes the new beer list into the shops json file.
    write_json(list,"json/" +  MODULE_NAME)

    return new_entries

def crawl(url):
    """Creates a list of Beer objects."""
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    list = []
    print(end='', flush=True)

    for element in soup.find_all("a", "butt_reszletes"):

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
                sub_soup = BeautifulSoup(requests.get("https://www.beerside.hu" + element['href']).text, "html.parser")
                beer = Beer()

                beer.link = "https://www.beerside.hu" + element['href']

                # The package, abv and style attributes are stored in one element and not always present.
                # Because of this the script evaluates both the value and the size of this element.
                package_abv_style = get_elements(get_element(sub_soup, "table", "shop_attributes"), "td")
                package_abv_style_size = len(package_abv_style)

                if package_abv_style_size > 1 and isinstance(package_abv_style, ResultSet):
                    beer.package = get_element_attribute(package_abv_style[0], "text").replace(" ", "")

                    if package_abv_style_size == 2:
                        beer.abv = re.search(r'[0-9]*\,*\.*[0-9]+[%]{1}', get_element_attribute(get_element(sub_soup, "h1", itemprop="name"), "text")).group(0).strip()
                        beer.style = get_element_attribute(package_abv_style[1], "text")
                    else:
                        beer.abv = get_element_attribute(package_abv_style[1], "text").replace(" ", "")
                        beer.style = get_element_attribute(package_abv_style[2], "text")
                else:
                    beer.package= NotAvailable.text
                    beer.abv = NotAvailable.text
                    beer.style = NotAvailable.text

                # The price and currency attributes are stored in one element.
                price_and_currency = get_element_attribute(get_element(sub_soup, "div", "termekar"), "text")

                if price_and_currency == NotAvailable.text:
                    beer.price = NotAvailable.text
                    beer.currency = NotAvailable.text
                else:
                    price_and_currency = price_and_currency.split("-")
                    beer.price = price_and_currency[0].replace(" ", "").strip()
                    beer.currency = price_and_currency[1].replace(" ", "").strip()

                # This shop does not states the country and the brewery as independent attribute.
                beer.country = NotAvailable.text
                beer.brewery = NotAvailable.text

                beer.name = get_formatted_name(get_element_attribute(get_element(sub_soup, "h1", itemprop="name"), "text"), beer.brewery)
                try_counter = 3
            except KeyboardInterrupt:
                raise
            # If there was an error sleeps for five seconds and adds one to the try_counter.
            except:
                time.sleep(5)
                try_counter = try_counter + 1

        list.append(beer.__dict__)
        print(".", end='', flush=True)

    return list