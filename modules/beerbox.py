from bs4 import BeautifulSoup
from modules.common import *
from math import ceil
import requests
import os
import time

MODULE_NAME = os.path.basename(__file__).replace(".py", "")
MANDATORY_COOKIE_NAME = "adult_only_accepted"
MANDATORY_COOKIE_VALUE = None
NUMBER_OF_BEERS_PER_PAGE = 21

def run():
    """The main function of the module."""
    log_and_print(get_lang_text("BROWSE_BEERBOX"))
    global MANDATORY_COOKIE_VALUE
    MANDATORY_COOKIE_VALUE = get_mandatory_cookie_value()
    list = []

    for page_number in range(1, ceil(ARGS.beercount / NUMBER_OF_BEERS_PER_PAGE) + 1):
        crawl("https://beerbox.hu/product-category/sorok-8?page={}".format(page_number), list)

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
    req = requests.get(url, cookies={MANDATORY_COOKIE_NAME:MANDATORY_COOKIE_VALUE})
    soup = BeautifulSoup(req.text, "html.parser")
    print(end='', flush=True)

    for element in soup.find_all("div", "single-product product-item text-center white-bg"):

        # If the set amount of beer is gathered breaks the crawl loop.
        if ARGS.beercount == len(list):
            break

        product_images = element.find("div", "product-images")

        # If the script is unable to find the beers image, skips to the next element.
        if product_images is None:
            continue

        sub_element = product_images.find('a')

        # If for some reason there is no link to go to the beers page, skips to the next element.
        if sub_element is None or 'href' not in sub_element.attrs:
            continue

        try_counter = 0

        # Tries the crawl up to three times to eliminate breaks caused by network errors.
        while try_counter < 3:
            try:
                sub_soup = BeautifulSoup(requests.get(sub_element['href'], cookies={MANDATORY_COOKIE_NAME:MANDATORY_COOKIE_VALUE}).text, "html.parser")
                beer = Beer()

                beer.link = sub_element['href']
                style_and_abv = get_element_attribute(get_element(sub_soup, "div", "product-content"), "text")
                abv = re.search(r'[0-9]*\,*\.*[0-9]+[%]{1}', style_and_abv)
                if abv is None:
                    beer.abv = NotAvailable.text
                else:
                    beer.abv = abv.group(0)

                beer.style = style_and_abv.replace(beer.abv, "").strip()
                set_package_brewery_country_attributes(sub_soup, beer)
                beer.name = get_formatted_name(get_element_attribute(get_element(sub_soup, "h3", "breadcum-page-title text-center"), "text"), beer.brewery)
                beer.price = get_element_attribute(get_element(get_element(sub_soup, "ul", "d-sm-flex align-items-sm-center"), "span"), "text").replace("Ft", "").replace(" ", "")
                beer.currency = "HUF"
                try_counter = 3
            except KeyboardInterrupt:
                raise
            # If there was an error sleeps for five seconds and adds one to the try_counter.
            except:
                time.sleep(5)
                try_counter = try_counter + 1

        list.append(beer.__dict__)
        print(".", end='', flush=True)

def get_mandatory_cookie_value():
    """Returns the cookie required to crawl the site."""
    session = requests.session()
    session.get("https://beerbox.hu/accept-adult-only")
    return requests.utils.dict_from_cookiejar(session.cookies).get(MANDATORY_COOKIE_NAME)

def set_package_brewery_country_attributes(sub_soup, beer):
    """The package, brewery and country attributes are stored in one element.
    This method breaks them apart and checks if they are present."""
    table_striped = get_element(sub_soup, "table", "table table-striped")

    if table_striped is NotAvailable:
        beer.package = NotAvailable.text
        beer.brewery = NotAvailable.text
        beer.country = NotAvailable.text
        return

    elements = get_elements(table_striped, "td")

    if elements is NotAvailable:
        beer.package = NotAvailable.text
        beer.brewery = NotAvailable.text
        beer.country = NotAvailable.text
    else:
        beer.package = get_element_attribute(elements[0], "text")
        beer.brewery = get_element_attribute(elements[1], "text")
        beer.country = get_element_attribute(elements[2], "text")